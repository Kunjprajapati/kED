from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import mimetypes
# import logging

# Importing all the DailyCharges Script Logic Files
from .scriptSRC.ORG_DailyCharges_FOR_CMC import function_for_CMC
from .scriptSRC.ORG_DailyCharges_FOR_CoolKidz import function_for_coolkidz
from .scriptSRC.ORG_DailyCharges_FOR_Gastroenterology_Atlanta import function_for_Gastroenterology_Atlanta
from .scriptSRC.ORG_DailyCharges_For_GUCFP import function_for_Gwinnett
from .scriptSRC.ORG_DailyCharges_FOR_Gulf import function_for_gulf
from .scriptSRC.ORG_DailyCharges_FOR_HPC import function_for_HPC
from .scriptSRC.ORG_DailyCharges_FOR_SMP import function_for_SMP
from .scriptSRC.ORG_DailyCharges_FOR_SWMD import function_for_SWMD
from .scriptSRC.ORG_DailyCharges_ShivDhara import function_for_shivDhara
from .scriptSRC.ORG_DailyCharges_FOR_Stone import function_for_stoneCharges
from .scriptSRC.ORG_DailyCharges_FOR_Thomas import function_for_Thomas
from .scriptSRC.ORG_DailyCharges_FOR_MAG import function_for_MAG
from .scriptSRC.ORG_DailyCharges_FOR_EIM import function_FOR_EIM
from .scriptSRC.ORG_DailyCharges_FOR_RPL import function_for_RPL


# Importing all the DailyEV Script Logic Files
from .scriptSRC.ORG_DailyEV_CMD import apply_logic_FOR_dailyEV_CMD
from .scriptSRC.ORG_DailyEV_Health_First import apply_logic_FOR_dailyEV_HealthFirst
from .scriptSRC.ORG_DailyEV_CoolKidz import apply_logic_FOR_dailyEV_CoolKidz
from .scriptSRC.ORG_DailyEV_MAG import apply_logic_FOR_dailyEV_MAG
from .scriptSRC.ORG_DailyEV_SWMD import apply_logic_FOR_dailyEV_SWMD
from .scriptSRC.ORG_DailyEV_BHO import apply_logic_FOR_dailyEV_BHO

# Importing all the AR Script Logic Files
from .scriptSRC.ORD_CoolKidz_AR import apply_logic_FOR_AR_CoolKidz
from .scriptSRC.ORG_Gestro_AR import apply_logic_FOR_AR_Gestro
from .scriptSRC.ORG_MAG_AR import apply_logic_FOR_AR_MAG
from .scriptSRC.ORG_CMD_AR import apply_logic_FOR_AR_CMD
from .scriptSRC.ORG_HPC_AR import apply_logic_FOR_AR_HPC
from .scriptSRC.ORG_SWMD_AR import apply_logic_FOR_AR_SWMD
from .scriptSRC.ORG_Oak_Hills_Family_Care_AR import apply_logic_FOR_AR_Oak_Hills_Preprocessing
from .scriptSRC.ORG_Gulf_AR import apply_logic_FOR_AR_Gulf

import logging

logger = logging.getLogger(__name__)

# Login View Page
def loginPage(request):
    return render(request, 'loginpage.html')

# Creating First View For "The Home Page"
def homePage(request):
    return render(request, 'mainpage.html')

# Importing the entire stuff of DailyCharges
def dailyChargesPage(request):
    return render(request, 'DailyCharges.html')

# Importing the entire stuff of DailyEV
def dailyEVPage(request):
    return render(request, 'DailyEV.html')

def ARPage(request):
    return render(request, 'AR.html')

# Importing all the core Logics & Upload function of DailyCharges
def cmc_dailychargesRenderFile(request):
    return render(request, 'DailyCharges_CMC.html')

def coolkidz_dailychargesRenderFile(request):
    return render(request, 'DailyCharges_coolkidz.html')

def GastroenterologyAtlanta_dailyChargesRenderFile(request):
    return render(request, 'DailyCharges_GastroenterologyAtlanta.html')

def Gwinnett_dailyChargesRenderFile(request):
    return render(request, 'DailyCharges_Gwinnett.html')

def Gulf_dailyChargesRenderFile(request):
    return render(request, 'DailyCharges_Gulf.html')

def HPC_dailyChargesRenderFile(request):
    return render(request, 'DailyCharges_HPC.html')

def SMP_dailyChargesRenderFile(request):
    return render(request, 'DailyCharges_SMP.html')

def SWMD_dailyChargesRenderFile(request):
    return render(request, 'DailyCharges_SWMD.html')

def Thomas_dailyChargesRenderFile(request):
    return render(request, 'DailyCharges_Thomas.html')

def ShivDhara_dailyChargesRenderFile(request):
    return render(request, 'DailyCharges_ShivDhara.html')

def Stone_dailyChargesRenderFile(request):
    return render(request, 'DailyCharges_Stone.html')

def MAG_dailyChargesRenderFile(request):
    return render(request, 'DailyCharges_MAG.html')

def EIM_dailyChargesRenderFile(request):
    return render(request, 'DailyCharges_EIM.html')

def RPL_dailyChargesRenderFile(request):
    return render(request, 'DailyCharges_RPL.html')

@csrf_exempt
def generate_file_view_charges(request):
    if request.method == 'POST' and request.FILES.get('excelFile'):
        excel_file = request.FILES['excelFile']
        action = request.POST.get('action')
        file_type, _ = mimetypes.guess_type(excel_file.name)
        logger.info(f"Uploaded file name: {excel_file.name}, File type: {file_type}")
                                                                                                                    
        # Allowing both Excel and CSV file types
        if file_type not in ['application/vnd.ms-excel', 
                             'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             'text/csv']:
            return JsonResponse({'error': 'Unsupported file type'}, status=400)

        try:
            saved_file_path = handle_uploaded_file_charges(excel_file)
            logger.info(f"Action: {action}, File saved at: {saved_file_path}")
            if saved_file_path:
                # Process the file based on the action
                if action == 'Coolkids':
                    result_path = function_for_coolkidz(saved_file_path)
                elif action == 'cmc':
                    result_path = function_for_CMC(saved_file_path)
                elif action == "GastroenterologyAtlanta":
                    result_path = function_for_Gastroenterology_Atlanta(saved_file_path)
                elif action == "Gwinnett":
                    result_path = function_for_Gwinnett(saved_file_path)
                elif action == "Gulf":
                    result_path = function_for_gulf(saved_file_path)
                elif action == "HPC":
                    result_path = function_for_HPC(saved_file_path)
                elif action == "SMP":
                    result_path = function_for_SMP(saved_file_path)
                elif action == "SWMD":
                    result_path = function_for_SWMD(saved_file_path)
                elif action == "ShivDhara":
                    result_path = function_for_shivDhara(saved_file_path)
                elif action == 'Stone':
                    result_path = function_for_stoneCharges(saved_file_path)
                elif action == "Thomas":
                    result_path = function_for_Thomas(saved_file_path)
                elif action == "MAG":
                    result_path = function_for_MAG(saved_file_path)
                elif action == "RPL":
                    result_path = function_for_RPL(saved_file_path)
                elif action == "EIM":
                    result_path = function_FOR_EIM(saved_file_path)
                else:
                    return JsonResponse({'error': 'Invalid action'}, status=400)

                if result_path:
                    with open(result_path, 'rb') as file:
                        response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(result_path)}"'
                        return response
                else:
                    logger.error('Failed to process file: No result path')
                    return JsonResponse({'error': 'Failed to process file'}, status=500)
            else:
                return JsonResponse({'error': 'Failed to save file'}, status=500)

        except Exception as e:
            logger.exception("Error processing file in generate_file_view_charges")
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'No file found in request'}, status=400)

def handle_uploaded_file_charges(file):
    try:
        upload_dir = 'uploaded_Charges_Files'
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

# Importing all the core Logics & Upload function of DailyEV
def CMD_DailyEVRenderFile(request):
    return render(request, 'DailyEV_CMD.html')

def HealthFirst_DailyEVRenderFile(request):
    return render(request, 'DailyEV_HealthFirst.html')

def Coolkids_DailyEVRenderFile(request):
    return render(request, 'DailyEV_Coolkidz.html')

def MAG_DailyEVRenderFile(request):
    return render(request, 'DailyEV_MAG.html')

def SWMD_DailyEVRenderFile(request):
    return render(request, 'DailyEV_SWMD.html')

def BHO_DailyEVRenderFile(request):
    return render(request, 'DailyEV_BHO.html')

@csrf_exempt
def generate_file_dailyEV(request):
    if request.method == 'POST' and request.FILES.get('excelFile1') and request.FILES.get('excelFile2'):
        excel_file1 = request.FILES['excelFile1']
        excel_file2 = request.FILES['excelFile2']
        action = request.POST.get('action')

        try:
            saved_file_path1 = handle_uploaded_file_EV(excel_file1)
            saved_file_path2 = handle_uploaded_file_EV(excel_file2)
            if saved_file_path1 and saved_file_path2:
                if action == 'CMD':
                    result_path = apply_logic_FOR_dailyEV_CMD(saved_file_path1, saved_file_path2)
                elif action == "HealthFirst":
                    result_path = apply_logic_FOR_dailyEV_HealthFirst(saved_file_path1, saved_file_path2)
                elif action == "Coolkidz":
                    result_path = apply_logic_FOR_dailyEV_CoolKidz(saved_file_path1, saved_file_path2)
                elif action == "MAG":
                    result_path = apply_logic_FOR_dailyEV_MAG(saved_file_path1, saved_file_path2)
                elif action == "SWMD":
                    result_path = apply_logic_FOR_dailyEV_SWMD(saved_file_path1, saved_file_path2)
                elif action == "BHO":
                    result_path = apply_logic_FOR_dailyEV_BHO(saved_file_path1, saved_file_path2)
                else:
                    return JsonResponse({'error': 'Invalid action. Please select a valid action.'}, status=400)

                if result_path:
                    with open(result_path, 'rb') as file:
                        response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(result_path)}"'
                        return response
                else:
                    logger.error('Failed to process file: No result path')
                    return JsonResponse({'error': 'Failed to process file'}, status=500)
            else:
                return JsonResponse({'error': 'Failed to save file'}, status=500)

        except Exception as e:
            logger.exception("Error processing file in generate_file_dailyEV")
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'No file found in request'}, status=400)

def handle_uploaded_file_EV(file):
    try:
        upload_dir = 'uploaded_files_EV'
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

# Importing all the core Logics & Upload function of AR
def Coolkidz_ARRenderFile(request):
    return render(request, 'AR_Coolkidz.html')

def GastroenterologyAtlanta_ARRenderFile(request):
    return render(request, 'AR_Gastro.html')

def MAG_ARRenderFile(request):
    return render(request, 'AR_MAG.html')

def CMD_ARRenderFile(request):
    return render(request, 'AR_CMD.html')

def HPC_ARRenderFile(request):
    return render(request, 'AR_HPC.html')

def SWMD_ARRenderFile(request):
    return render(request, 'AR_SWMD.html')

def Oak_Hills_ARRenderFile(request):
    return render(request, 'AR_Oak_Hills.html')

def Gulf_ARRenderFile(request):
    return render(request, 'AR_Gulf.html')

@csrf_exempt
def generate_file_AR(request):
    if request.method == 'POST' and request.FILES.get('excelFile1') and request.FILES.get('excelFile2'):
        excel_file1 = request.FILES['excelFile1']
        excel_file2 = request.FILES['excelFile2']
        action = request.POST.get('action')

        try:
            saved_file_path1 = handle_uploaded_file_AR(excel_file1)
            saved_file_path2 = handle_uploaded_file_AR(excel_file2)
            if saved_file_path1 and saved_file_path2:
                zip_file_path = None
                logger.info(f"Action: {action}")
                print(f"_______________________________________________{action}_______________________________________________")
                if action == "CMD":
                    zip_file_path = apply_logic_FOR_AR_CMD(saved_file_path1, saved_file_path2)
                elif action == 'Coolkidz':
                    zip_file_path = apply_logic_FOR_AR_CoolKidz(saved_file_path1, saved_file_path2)
                elif action == "GastroenterologyAtlanta":
                    zip_file_path = apply_logic_FOR_AR_Gestro(saved_file_path1, saved_file_path2)
                elif action == "MAG":
                    zip_file_path = apply_logic_FOR_AR_MAG(saved_file_path1, saved_file_path2)
                elif action == "HPC":
                    zip_file_path = apply_logic_FOR_AR_HPC(saved_file_path1, saved_file_path2)
                elif action == "SWMD":
                    zip_file_path = apply_logic_FOR_AR_SWMD(saved_file_path1, saved_file_path2)
                elif action == "Oak Hills":
                    zip_file_path = apply_logic_FOR_AR_Oak_Hills_Preprocessing(saved_file_path1, saved_file_path2)
                elif action == "Gulf":
                    zip_file_path = apply_logic_FOR_AR_Gulf(saved_file_path1, saved_file_path2)
                else:
                    return JsonResponse({'error': 'Invalid action. Please select a valid action.'}, status=400)

                if zip_file_path:
                    with open(zip_file_path, 'rb') as f:
                        response = HttpResponse(f.read(), content_type='application/zip')
                        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(zip_file_path)}"'
                        
                        return response
                else:
                    logger.error('No zip file generated')
                    return JsonResponse({'error': 'No zip file generated'}, status=400)
            else:
                return JsonResponse({'error': 'Failed to save uploaded files'}, status=400)
        except Exception as e:
            logger.exception("Error processing file in generate_file_AR")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'No file found in request'}, status=400)

def handle_uploaded_file_AR(file):
    try:
        upload_dir = 'uploaded_files_AR'
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
    



# View for logs
def logs_view(request):
    # Replace this with your actual logic to retrieve logs
    logs = [
        "Log entry 1: User logged in.",
        "Log entry 2: File uploaded successfully.",
        "Log entry 3: Error processing request.",
    ]
    return render(request, 'logs.html', {'logs': logs})
