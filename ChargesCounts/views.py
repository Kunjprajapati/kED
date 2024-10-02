import os
import mimetypes
import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import pandas as pd

# Import your script logic modules here
from .chargesCountScripts.chargeCounts import ORG_chargesCounts, MorningStoneChargesCounts, EveningStoneChargesCounts

logger = logging.getLogger(__name__)

def homePage(request):
    return render(request, "ChargeCounts.html")

@csrf_exempt
def generate_file_ChargesCounts(request):
    logger.debug(f"POST data: {request.POST}")
    logger.debug(f"Files data: {request.FILES}")    
    excel_file = request.FILES.get('excelFile')
    if not excel_file:
        return JsonResponse({'error': 'No file found in request'}, status=400)
    if request.method == 'POST' and request.FILES.get('excelFile'):
        excel_file = request.FILES['excelFile']
        action = request.POST.get('action')
        file_type, _ = mimetypes.guess_type(excel_file.name)
        
        if file_type not in ['application/vnd.ms-excel', 
                             'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             'text/csv']:
            return JsonResponse({'error': 'Unsupported file type'}, status=400)

        try:
            saved_file_path = handle_uploaded_file(excel_file)
            if saved_file_path:
                print("___________________________________________________________________")
                result_path = ORG_chargesCounts(saved_file_path) 
                if result_path:
                    return serve_file_response(result_path)
                else:
                    logger.error('Failed to process file: No result path')
                    return JsonResponse({'error': 'Failed to process file'}, status=500)
            else:
                return JsonResponse({'error': 'Failed to save file'}, status=500)
        except Exception as e:
            logger.exception("Error processing file in generate_file_ChargesCounts")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'No file found in request'}, status=400)

def handle_uploaded_file(file):
    try:
        upload_dir = 'uploaded_files'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        file_path = os.path.join(upload_dir, file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return file_path
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None

def serve_file_response(file_path):
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response

def counts_view(request):
    morning_counts = {}
    evening_counts = {}

    if request.method == 'POST' and request.FILES.get('csv_file'):
        # Handle file upload
        uploaded_file = request.FILES['csv_file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)  # Save the uploaded file
        file_path = fs.url(filename)  # Get the file path

        # Call ORG_chargesCounts to process the uploaded CSV file
        output_file_path = ORG_chargesCounts(file_path)  # Process the uploaded file

        # Read the output file into a DataFrame
        data = pd.read_excel(output_file_path, engine='openpyxl')

        # Get morning and evening counts
        morning_counts = MorningStoneChargesCounts(data)
        evening_counts = EveningStoneChargesCounts(data)

    return render(request, 'ChargeCounts.html', {
        'morning_counts': morning_counts,
        'evening_counts': evening_counts,
    })