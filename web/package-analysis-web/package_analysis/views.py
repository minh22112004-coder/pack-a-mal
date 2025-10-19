from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import PackageSubmitForm

from .helper import Helper
import json

from django.core.files.storage import FileSystemStorage

from .models import Package, ReportDynamicAnalysis, APIKey, AnalysisTask
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from .src.py2src.py2src.url_finder import   URLFinder
from .utils import PURLParser, validate_purl_format
from .auth import require_api_key
from django.utils import timezone
from django.urls import reverse



def save_report(reports):

    package, created = Package.objects.get_or_create(
        package_name=reports['packages']['package_name'],
        package_version=reports['packages']['package_version'],
        ecosystem=reports['packages']['ecosystem']
    )
    report = ReportDynamicAnalysis.objects.create(
        package=package,
        time=reports['time'],
        report=reports
    )
    report.save()



def dashboard(request):
    form = PackageSubmitForm()
    return render(request, 'package_analysis/dashboard.html', {'form': form})

def contact(request):
    return render(request, 'package_analysis/homepage/contact.html')
 
def homepage(request):
    return render(request, 'package_analysis/homepage/homepage.html')

def dynamic_analysis(request):
    # this tool using package-analysis tools to analyze the package.
    if request.method == 'POST':
        print("dynamic analysis Post ^^^^")
        form = PackageSubmitForm(request.POST)
        if form.is_valid():
            print("dynamic analysis form is valid")
            package_name = form.cleaned_data['package_name']
            package_version = form.cleaned_data['package_version']
            ecosystem = form.cleaned_data['ecosystem']

            # Process the form data (e.g., save to database, call an API, etc.)
            print(f"Package Name: {package_name}, Package Version: {package_version}, Ecosystem: {ecosystem}")
            reports = Helper.run_package_analysis(package_name, package_version, ecosystem)
            return JsonResponse({"dynamic_analysis_report": reports})

    form = PackageSubmitForm()
    return render(request, 'package_analysis/analysis/dynamic_analysis.html', {'form': form}) 

def malcontent(request):
    if request.method == 'POST':
        form = PackageSubmitForm(request.POST)
        if form.is_valid():
            package_name = form.cleaned_data['package_name']
            package_version = form.cleaned_data['package_version']
            ecosystem = form.cleaned_data['ecosystem']
            
            reports = Helper.run_malcontent(package_name, package_version, ecosystem)
            return JsonResponse({"malcontent_report": reports})
    form = PackageSubmitForm()
    return render(request, 'package_analysis/analysis/malcontent.html', {'form': form})

def lastpymile(request):
    if request.method == 'POST':
        print("lastpymile Post ^^^^")
        form = PackageSubmitForm(request.POST)
        if form.is_valid():
            print("lastpymile form is valid")
            package_name = form.cleaned_data['package_name']
            package_version = form.cleaned_data['package_version']
            ecosystem = form.cleaned_data['ecosystem']

            # Process the form data (e.g., save to database, call an API, etc.)
            print(f"Package Name: {package_name}, Package Version: {package_version}, Ecosystem: {ecosystem}")
            reports = Helper.run_lastpymile(package_name, package_version, ecosystem)
            return JsonResponse({"lastpymile_report": reports})
    form = PackageSubmitForm()
    return render(request, 'package_analysis/analysis/lastpymile.html', {'form': form})

def bandit4mal(request):
    print("submit static analysis bandit4mal tools")
    if request.method == 'POST':
        form = PackageSubmitForm(request.POST)
        if form.is_valid():
            print("bandit4mal form is valid")
            package_name = form.cleaned_data['package_name']
            package_version = form.cleaned_data['package_version']
            ecosystem = form.cleaned_data['ecosystem']

            # Process the form data (e.g., save to database, call an API, etc.)
            print(f"Package Name: {package_name}, Package Version: {package_version}, Ecosystem: {ecosystem}")
            reports = Helper.run_bandit4mal(package_name, package_version, ecosystem)
            return JsonResponse({"bandit4mal_report": reports})
    form = PackageSubmitForm()
    return render(request, 'package_analysis/analysis/bandit4mal.html', {'form': form})

def find_typosquatting(request):
    print("find typosquatting")
    if request.method == 'POST':
        form = PackageSubmitForm(request.POST)
        if form.is_valid():
            package_name = form.cleaned_data['package_name']
            package_version = form.cleaned_data['package_version']
            ecosystem = form.cleaned_data['ecosystem']

            # Process the form data (e.g., save to database, call an API, etc.)
            print(f"find oss-squat:package Name: {package_name}, Package Version: {package_version}, Ecosystem: {ecosystem}")
            typo_candidates = Helper.run_oss_squats(package_name, package_version, ecosystem)
            print("Typo candidates: ", typo_candidates)
            return JsonResponse({'typosquatting_candidates': typo_candidates})
        
    form = PackageSubmitForm()
    return render(request, 'package_analysis/analysis/typosquatting.html', {'form': form})

def find_source_code(request):
    if request.method == 'POST':
        print("find source code")
        form = PackageSubmitForm(request.POST)
        if form.is_valid():
            print("find source code form is valid")
            package_name = form.cleaned_data['package_name']
            package_version = form.cleaned_data['package_version']
            ecosystem = form.cleaned_data['ecosystem']

            # Process the form data (e.g., save to database, call an API, etc.)
            if ecosystem == "pypi":
                sources = Helper.run_py2src(package_name, package_version, ecosystem)
            else: 
                urls = Helper.run_oss_find_source(package_name, package_version, ecosystem)
                sources = []
                for url in urls:
                    if url != "" and URLFinder.test_url_working(URLFinder.normalize_url(url)):
                        sources.append(URLFinder.real_github_url(url))

                sources = list(set(sources))
        

            return JsonResponse({'source_urls': sources})
        
    form = PackageSubmitForm()
    return render(request, 'package_analysis/analysis/findsource.html', {'form': form})

def submit_sample(request):
    # TODO: if package has already been analyzed, return the report instead of re-analyzing it.

    ''' Enter package name, version and ecosystem to analyze the package.
      The package are already in the Wolfi registry'''
    if request.method == 'POST':
        form = PackageSubmitForm(request.POST)
        if form.is_valid():

            package_name = form.cleaned_data['package_name']
            package_version = form.cleaned_data['package_version']
            ecosystem = form.cleaned_data['ecosystem']
            # Process the form data (e.g., save to database, call an API, etc.)
            print(f"Package Name: {package_name}, Package Version: {package_version}, Ecosystem: {ecosystem}")

            with ThreadPoolExecutor() as executor:
                future_reports = executor.submit(Helper.run_package_analysis, package_name, package_version, ecosystem)
                future_typosquatting_candidates = executor.submit(Helper.run_oss_squats, package_name, package_version, ecosystem)
                future_sources = executor.submit(Helper.run_oss_find_source, package_name, package_version, ecosystem)

                reports = future_reports.result()
                typo_candidates = future_typosquatting_candidates.result()
                sources = future_sources.result()

                reports['sources'] = sources
                reports['typo_candidates'] = typo_candidates

                print("Typo candidates: ", reports['typo_candidates'])

            
            # save_report(reports)
            latest_report = Report.objects.latest('id')
            reports['id'] = latest_report.id
            return JsonResponse(reports)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def upload_sample(request):
    ''' Upload sample  analysis it'''
    if request.method == 'POST' and request.FILES['file']:
         
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        uploaded_file_url = fs.url(filename)
        ecosystem = request.POST.get('ecosystem', None)
        package_name = request.POST.get('package_name', None)
        package_version = request.POST.get('package_version', None)
        
        reports = Helper.handle_uploaded_file(uploaded_file_url, package_name, package_version, ecosystem)
        
        # Save to database
        # save_report(reports)
        # latest_report = Report.objects.latest('id')
        # reports['id'] = latest_report.id
        # delete the uploaded file
        fs.delete(filename)
        return JsonResponse({"dynamic_analysis_report": reports})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    


def report_detail(request, report_id):
    '''Report detail analysis result of the package'''
    report = Report.objects.get(pk=report_id)
    return render(request, 'package_analysis/report_detail.html', {'report': report})

def get_all_report(request):
    report = Report.objects.all()
    results = {}
    for r in report:
        results[r.id] = {
            'id': r.id,
            'package_name': r.package.package_name,
            'package_version': r.package.package_version,
            'ecosystem': r.package.ecosystem,
            'time': r.time,
        }

    return JsonResponse(results)

def get_report(request, report_id):
    report = Report.objects.get(pk=report_id)
    results = {
        'package_name': report.package.package_name,
        'package_version': report.package.package_version,
        'ecosystem': report.package.ecosystem,
        'time': report.time,
        'num_files': report.num_files,
        'num_commands': report.num_commands,
        'num_network_connections': report.num_network_connections,
        'num_system_calls': report.num_system_calls,
        'files': report.files,
        'dns': report.dns,
        'ips': report.ips,
        'commands': report.commands,
        'syscalls': report.syscalls,
    }
    return JsonResponse(results)

def analyzed_samples(request):
    '''List of analyzed samples, sorted by id'''

    packages = Package.objects.all().order_by('-id')

    return render(request, 'package_analysis/analyzed_samples.html', {'packages': packages})

def get_wolfi_packages(request):
    return JsonResponse(Helper.get_wolfi_packages())

def get_maven_packages(request):
    return JsonResponse(Helper.get_maven_packages())

def get_rust_packages(request):
    return JsonResponse(Helper.get_rust_packages())

def get_pypi_packages(request):
    return JsonResponse(Helper.get_pypi_packages() )

def get_npm_packages(request):
    return JsonResponse(Helper.get_npm_packages())

@staticmethod
def get_packagist_packages(request):
    return JsonResponse(Helper.get_packagist_packages())

@staticmethod
def get_rubygems_packages(request):
    return JsonResponse(Helper.get_rubygems_packages())

@staticmethod
def get_rubygems_versions(request):
    import requests
    def get_package_versions(package_name):
        url = f"https://rubygems.org/api/v1/versions/{package_name}.json"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results = []
            for version in data:
                results.append(version['number'])
            return results
        else:
            return []
        
    package_name = request.GET.get('package_name', None)
    if not package_name:
        return JsonResponse({'error': 'Package name is required'}, status=400)
    
    get_package_versions = get_package_versions(package_name)
    return JsonResponse({"versions": get_package_versions})

@staticmethod
def get_packagist_versions(request):
    import requests
    def get_package_versions(package_name):
        url = f"https://repo.packagist.org/p2/{package_name}.json"
        print("get_packagist_versions url: ", url)

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            results = []
            for version in data['packages'].get(package_name, []):
                results.append(version['version'])
            return results
        else:
            return []  # Return an empty list if the request fails
    
    package_name = request.GET.get('package_name', None)
    if not package_name:
        return JsonResponse({'error': 'Package name is required'}, status=400)
    
    package_versions = get_package_versions(package_name)
    return JsonResponse({"versions": package_versions})



       
           



def get_npm_versions(request):
    import requests
    def get_package_versions(package_name):
        url = f'https://registry.npmjs.org/{package_name}'
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            versions = list(data.get('versions', {}).keys())
            latest_version = data.get('dist-tags', {}).get('latest')
            
            return versions
        else:
            print(f"Failed to fetch {package_name}: {response.status_code}")
            return None
        
    package_name = request.GET.get('package_name', None)
    if not package_name:
        return JsonResponse({'error': 'Package name is required'}, status=400)
    
    package_versions = get_package_versions(package_name)
    return JsonResponse({"versions": package_versions})

def get_pypi_versions(request):
    package_name = request.GET.get('package_name', None)
    if not package_name:
        return JsonResponse({'error': 'Package name is required'}, status=400)
    
    import requests
    def get_versions(package_name):
        """Get all available versions of a package from PyPI."""
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            versions = list(data['releases'].keys())  # Directly convert to list
            return versions
        else:
            return []  # Return empty list if request fails
         
    # Get the versions of the package
    versions = get_versions(package_name)

    return JsonResponse({"versions":versions})


@csrf_exempt
@require_api_key
def analyze_api(request):
    """
    API endpoint to analyze packages via PURL
    Accepts POST requests with PURL in JSON body
    Returns analysis task ID and result URL
    """
    if request.method != 'POST':
        return JsonResponse({
            'error': 'Method not allowed',
            'message': 'Only POST requests are supported'
        }, status=405)
    
    try:
        # Parse JSON request body
        data = json.loads(request.body)
        purl = data.get('purl')
        
        if not purl:
            return JsonResponse({
                'error': 'Missing PURL',
                'message': 'PURL parameter is required'
            }, status=400)
        
        # Validate PURL format
        if not validate_purl_format(purl):
            return JsonResponse({
                'error': 'Invalid PURL format',
                'message': 'PURL must be a valid package URL starting with pkg:'
            }, status=400)
        
        # Parse PURL to extract package information
        try:
            package_name, package_version, ecosystem = PURLParser.extract_package_info(purl)
        except ValueError as e:
            return JsonResponse({
                'error': 'PURL parsing failed',
                'message': str(e)
            }, status=400)
        
        # Check for existing tasks (completed, running, or pending) within the last 24 hours
        existing_tasks = AnalysisTask.objects.filter(
            purl=purl,
            created_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).order_by('-created_at')
        
        # Debug: Print existing tasks for troubleshooting
        print(f"DEBUG: Found {existing_tasks.count()} existing tasks for PURL: {purl}")
        for task in existing_tasks:
            print(f"  Task {task.id}: status={task.status}, created={task.created_at}")
        
        # Check for completed task first
        completed_task = existing_tasks.filter(status='completed').first()
        if completed_task and completed_task.report:
            # Return existing analysis result
            result_url = request.build_absolute_uri(
                reverse('get_report', args=[completed_task.report.id])
            )

            # Save the completed analysis report as a downloadable JSON file on the server,

            import os
            from django.conf import settings

            # Extract the report data from the JSONField
            report_data = completed_task.report
            if hasattr(report_data, 'report'):
                # If it's a ReportDynamicAnalysis object, get the report field
                report_json = report_data.report
            else:
                # If it's already the report data
                report_json = report_data

            # Define a directory to save JSON files (e.g., MEDIA_ROOT/analysis_reports/)
            save_dir = getattr(settings, 'MEDIA_ROOT', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media'))
            reports_subdir = os.path.join(save_dir, 'analysis_reports')
            os.makedirs(reports_subdir, exist_ok=True)

            # Save JSON with a unique filename per report (e.g., by report id)
            json_filename = f"report_{completed_task.report.id}.json"
            json_path = os.path.join(reports_subdir, json_filename)

            # Save the file
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_json, f, ensure_ascii=False, indent=2)

            # Optionally, generate a URL for user access
            # This assumes MEDIA_URL is configured, and files are served from MEDIA_ROOT
            media_url = getattr(settings, 'MEDIA_URL', '/media/')
            download_url = request.build_absolute_uri( 
                os.path.join(media_url, 'analysis_reports', json_filename)
            )

            # Add download_url to the response

            return JsonResponse({
                'task_id': completed_task.id,
                'status': 'completed',
                'result_url': download_url,
                'message': 'Analysis already exists (cached result)'
            })
        
        # Check for running or pending task
        active_task = existing_tasks.filter(status__in=['running', 'pending']).first()
        if active_task:
            return JsonResponse({
                'task_id': active_task.id,
                'status': active_task.status,
                'result_url': request.build_absolute_uri(
                    reverse('task_status_api', args=[active_task.id])
                ),
                'message': f'Analysis already {active_task.status}'
            })
        
        # Final check before creating task (prevent race conditions)
        last_check = AnalysisTask.objects.filter(
            purl=purl,
            status__in=['pending', 'running'],
            created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
        ).first()
        
        if last_check:
            return JsonResponse({
                'task_id': last_check.id,
                'status': last_check.status,
                'result_url': request.build_absolute_uri(
                    reverse('task_status_api', args=[last_check.id])
                ),
                'message': f'Analysis already {last_check.status} (race condition prevented)'
            })
        
        # Create new analysis task
        task = AnalysisTask.objects.create(
            api_key=request.api_key,
            purl=purl,
            package_name=package_name,
            package_version=package_version,
            ecosystem=ecosystem,
            status='pending'
        )
        
        print(f"DEBUG: Created new task {task.id} for PURL: {purl}")
        
        # Start analysis asynchronously
        try:
            # Run analysis in background thread
            from threading import Thread
            
            def run_analysis():
                try:
                    task.status = 'running'
                    task.started_at = timezone.now()
                    task.save()
                    
                    # Run the analysis using existing Helper methods
                    with ThreadPoolExecutor() as executor:
                        future_reports = executor.submit(Helper.run_package_analysis, package_name, package_version, ecosystem)

                        reports = future_reports.result()
                    
                    # Save the report
                    # TODO: correct save_report function to match with the, the structure of saved folder is :
                    # 
                    # TODO 1 : the dynamic analysis report should be save as jon file in server side
                    # TODO 2: the json response to client will provide the url of the json file on the server side
                    # TODO 3: beside the link, it also include all the json repports except system calls, but instead, including the frequency of system call names enter
                    # TODO 4: we only save the information of packages: name, version, ecosystem,
                    #  date of the latest analysis, 
                     
                    # Helper.run_package_analysis function
                    save_report(reports)
                    latest_report = ReportDynamicAnalysis.objects.latest('id')
                    
                    # Update task with completed status
                    task.status = 'completed'
                    task.completed_at = timezone.now()
                    task.report = latest_report
                    task.save()
                    
                except Exception as e:
                    # Update task with error status
                    task.status = 'failed'
                    task.error_message = str(e)
                    task.completed_at = timezone.now()
                    task.save()
            
            # Start analysis thread
            analysis_thread = Thread(target=run_analysis)
            analysis_thread.daemon = True
            analysis_thread.start()
            
            # Return task information
            result_url = request.build_absolute_uri(
                reverse('task_status_api', args=[task.id])
            )
            
            return JsonResponse({
                'task_id': task.id,
                'status': 'pending',
                'result_url': result_url,
                'message': 'Analysis started successfully'
            })
            
        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.completed_at = timezone.now()
            task.save()
            
            return JsonResponse({
                'error': 'Analysis failed',
                'message': str(e),
                'task_id': task.id
            }, status=500)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON',
            'message': 'Request body must be valid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_api_key
def task_status_api(request, task_id):
    """
    API endpoint to check analysis task status
    """
    try:
        task = AnalysisTask.objects.get(id=task_id, api_key=request.api_key)
        
        response_data = {
            'task_id': task.id,
            'purl': task.purl,
            'status': task.status,
            'created_at': task.created_at.isoformat(),
            'package_name': task.package_name,
            'package_version': task.package_version,
            'ecosystem': task.ecosystem
        }
        
        if task.started_at:
            response_data['started_at'] = task.started_at.isoformat()
        
        if task.completed_at:
            response_data['completed_at'] = task.completed_at.isoformat()
        
        if task.error_message:
            response_data['error_message'] = task.error_message
        
        if task.status == 'completed' and task.report:
            response_data['result_url'] = request.build_absolute_uri(
                reverse('get_report', args=[task.report.id])
            )
        
        return JsonResponse(response_data)
        
    except AnalysisTask.DoesNotExist:
        return JsonResponse({
            'error': 'Task not found',
            'message': 'Analysis task not found or access denied'
        }, status=404)
   


def configure(request):
    return render(request, "package_analysis/configureSubmit.html")

def analyze(request):
    return render(request, "package_analysis/analyzing.html")

def results(request):
    return render(request, "package_analysis/reports.html")



