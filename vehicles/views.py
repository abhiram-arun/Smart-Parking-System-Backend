from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import VehicleLog
from django.utils import timezone
import pandas as pd
import os

@csrf_exempt
def vehicle_entry(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        plate = data.get('plate_number')
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'authorised_vehicles.csv')
        df = pd.read_csv(csv_path)
        authorised_plates = df['plate_number'].tolist()
       
        is_authorised = plate in authorised_plates 

        VehicleLog.objects.create(plate_number=plate, authorised=is_authorised)
        return JsonResponse({'status': 'entry logged', 'authorised': is_authorised})

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