from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import VehicleLog
from django.utils import timezone

@csrf_exempt
def vehicle_entry(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        plate = data.get('plate_number')
        VehicleLog.objects.create(plate_number=plate)
        return JsonResponse({'status': 'entry logged'})

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
    logs = VehicleLog.objects.all().values('plate_number', 'entry_time', 'exit_time')
    return JsonResponse(list(logs), safe=False)