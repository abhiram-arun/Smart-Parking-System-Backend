from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import VehicleLog
from django.utils import timezone
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def vehicle_entry(request):
    if request.method == 'POST':
        try:
            logger.info("Request body: %s", request.body)
            data = json.loads(request.body)
            plate = data.get('plate_number')

            if not plate:
                return JsonResponse({'error': 'Missing plate_number'}, status=400)

            csv_path = os.path.join(os.path.dirname(__file__), '..', 'authorised_vehicles.csv')
            csv_path = os.path.abspath(csv_path)

            logger.info(f"Reading CSV from: {csv_path}")
            df = pd.read_csv(csv_path)

            authorised_plates = df['plate_number'].tolist()
            is_authorised = plate in authorised_plates

            VehicleLog.objects.create(plate_number=plate, authorised=is_authorised)
            return JsonResponse({'status': 'entry logged', 'authorised': is_authorised})

        except json.JSONDecodeError:
            logger.exception("Invalid JSON")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        except FileNotFoundError:
            logger.exception("CSV file not found")
            return JsonResponse({'error': 'CSV file not found'}, status=500)

        except Exception as e:
            logger.exception("Unexpected error")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def vehicle_exit(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        plate = data.get('plate_number')
        try:
            log = VehicleLog.objects.filter(plate_number=plate, exit_time__isnull=True).latest('entry_time')
            log.exit_time = timezone.now()
            log.save()
            return JsonResponse({'status': 'exit logged'})
        except VehicleLog.DoesNotExist:
            return JsonResponse({'error': 'No active entry found'}, status=404)


def vehicle_logs(request):
    logs = VehicleLog.objects.all().order_by('-entry_time')
    data = [
        {
            'plate_number': log.plate_number,
            'entry_time': log.entry_time,
            'exit_time': log.exit_time,
            'authorised': log.authorised 
        }
        for log in logs
    ]
    return JsonResponse({'logs': data})