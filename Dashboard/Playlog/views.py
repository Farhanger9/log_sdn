
import csv
from datetime import datetime,time,date,timedelta
from django.shortcuts import render,HttpResponse
from .models import PlayLog,Campaign,Player
from pathlib import Path
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
import os
from django.db.models import Q
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

import threading
from django.http import StreamingHttpResponse
import sys
from time import sleep
sys.path.append('C:\WORKSPACE\WORKSPACE')
from main import *
from utils import *


def import_csv(current_date=None):

    DIR = Path(os.path.abspath(os.path.join(os.path.dirname('Dashboard'), '..')))
    if current_date==None:
        # Get the current date
        current_date = date.today()
        current_datetime=datetime.now()

    # Original file name
    file_name = "playlog-2023-05-23_readable.csv"

    # Extract the file name without the extension
    base_name = os.path.splitext(file_name)[0]

    # Create the new file name with the current date
    new_file_name = base_name.replace("2023-05-23", str(current_date)) + ".csv"
    file_path = os.path.join(DIR, f'log-report\\{new_file_name}')

    print(file_path)
    if os.path.exists(file_path):
        pass
    else:
        # Subtract a day from the current date
        previous_date = current_datetime - timedelta(days=1)
        # Create the new file name with the current date
        new_file_name = base_name.replace("2023-05-23", previous_date.strftime("%Y-%m-%d")) + ".csv"
        file_path = os.path.join(DIR, f'log-report\\{new_file_name}')


    index_file = os.path.join(DIR, f'log-report\\last_index_{current_date}.txt')

    print(file_path)

    if os.path.exists(file_path)==False:
        return
    print("saving data")

    # Read the last processed row index from the index file, or start from the beginning if the file doesn't exist
    if os.path.exists(index_file):
        with open(index_file, 'r') as f:
            last_index = int(f.read())
    else:
        last_index = 0

    # Read the CSV file in batches of 1000 rows, starting from the last processed row index
    with open(file_path) as f:
        reader = csv.reader(f)
        header = next(reader)  # Read the header row
        for _ in range(last_index):
            next(reader)  # Skip rows up to the last processed index

        batch = []
        campaign_names = set()
        player_names= set()
        for index, row in enumerate(reader, last_index + 1):
            player_name = row[0]
            end_time = row[1]
            duration = row[2]
            ad_copy_name = row[3]
            Number_of_Screens = row[4]
            campaign_name = row[5]
            Frame_Name = row[6]
            Display_Unit_Name = row[7]
            Impressions = row[8]
            Interactions = row[9]
            Extra_Data = row[10]
            variable = row[11]

            # Create Campaign object if it doesn't exist
            campaign_names.add(campaign_name)
            player_names.add(player_name)

            batch.append(row)

            if index % 1000 == 0:
                # Create Campaign objects in bulk
                campaigns = {}
                for name in campaign_names:
                    campaign, _ = Campaign.objects.get_or_create(name=name)
                    campaigns[name]=campaign
                players = {}
                for name in player_names:
                    player, _ = Player.objects.get_or_create(name=name)
                    players[name] = player

                # Create PlayLog objects from the current batch
                logs = []

                for row in batch:
                    if row[0]=="" or row[5]=="":
                        continue
                    else:
                        playlog = PlayLog(
                            player=players[row[0]],
                            end_time=row[1],
                            duration=row[2],
                            ad_copy_name=row[3],
                            Number_of_Screens=row[4],
                            campaign=campaigns[row[5]],
                            Frame_Name=row[6],
                            Display_Unit_Name=row[7],
                            Impressions=int(row[8]),
                            Interactions=int(row[9]),
                            Extra_Data=row[10],
                            variable=row[11]
                        )
                        logs.append(playlog)

                # Insert the PlayLog objects into the database
                PlayLog.objects.bulk_create(logs)

                # Reset the batch and campaign names set
                batch = []
                campaign_names = set()
                player_names = set()

                # Update the last processed row index in the index file
                with open(index_file, 'w') as f:
                    f.write(str(index))

        # Insert any remaining rows into the database
        if batch:
            campaigns = {}
            for name in campaign_names:
                campaign, _ = Campaign.objects.get_or_create(name=name)
                campaigns[name] = campaign
            players = {}
            for name in player_names:
                player, _ = Player.objects.get_or_create(name=name)
                players[name] = player

            logs = []
            for row in batch:
                if row[0] == "" or row[5] == "":
                    continue
                else:
                    playlog = PlayLog(
                        player=players[row[0]],
                        end_time=row[1],
                        duration=row[2],
                        ad_copy_name=row[3],
                        Number_of_Screens=row[4],
                        campaign=campaigns[row[5]],
                        Frame_Name=row[6],
                        Display_Unit_Name=row[7],
                        Impressions=int(row[8]),
                        Interactions=int(row[9]),
                        Extra_Data=row[10],
                        variable=row[11]
                    )
                    logs.append(playlog)

            PlayLog.objects.bulk_create(logs)

            # Update the last processed row index in the index file
            with open(index_file, 'w') as f:
                f.write(str(index))

    os.remove(index_file)
    print("Data saved")
    return HttpResponse('SUCCESS')
def get_all_threads():
    while True:
        status, links = get_all_playlogs()
        print("Running")
        if status == True:
            try:
                file=open("history.txt","r")
                history = [x.replace("\n","") for x in file.readlines()]
                file.close()

            except:
                file=open("history.txt","w")
                file.close()
                history=[]
            for link in links:
                if link in history:
                    continue
                date = link.split("playlog-")[1].replace(".gz", "").replace(".txt","")
                print(date)
                page_obj = PlayLog.objects.filter(end_time__startswith=date)

                if page_obj:
                    print(f"data exist for {date}")
                    continue
                # s = threading.Thread(target=import_csv)
                # s.start()
                update_id_label()
                build_table(date)
                print("build table done")
                s = threading.Thread(target=import_csv, args=(date,))
                s.start()
                s.join()
                history.append(link)
                file=open("history.txt","a")
                for h in history:
                    file.writelines(h+"\n")
                file.close()
                # break
        sleep(10)
def get_all(request):

    s=threading.Thread(target=get_all_threads)
    s.start()
    return HttpResponse("Bot notified data will be available in few minutes")
def get_data(request):

    date=request.GET['date']
    date = datetime.strptime(date, '%Y-%m-%d').date()
    print(date)
    page_obj = PlayLog.objects.filter(end_time__startswith=date)

    if page_obj:
        return HttpResponse("Data is available")
    # s = threading.Thread(target=import_csv)
    # s.start()
    build_table(date)
    print("builf table done")
    s=threading.Thread(target=import_csv,args=(date,))
    s.start()
    return HttpResponse("Bot notified data will be available in few minutes")
@login_required
def PlaylogList(request):
    # import_csv()
    s=threading.Thread(target=import_csv)
    s.start()
    # Convert start_date and end_date to datetime objects
    end_datetime = datetime.now().date() - timedelta(days=2)
    start_datetime = datetime.now().date() - timedelta(days=3)

    # Query the model using start and end dates
    page_obj = PlayLog.objects.filter(
        end_time__range=[start_datetime, end_datetime]
    ).select_related('campaign', 'player')

    start_date_str = start_datetime.strftime("%Y-%m-%d")
    end_datetime_str = end_datetime.strftime("%Y-%m-%d")

    page_number = request.GET.get('page')
    paginator = Paginator(page_obj, 20)
    page_obj = paginator.get_page(page_number)
    count_data = page_obj.paginator.count
    return render(request, 'dashboard.html', {'page_obj': page_obj,"start_date":start_date_str,
                                              "end_date":end_datetime_str,
                                              "count_data":count_data})

@login_required
def search(request):
    query = request.GET.get('query') or ''
    page_number = request.GET.get('page')
    context = PlayLog.objects.filter(Q(player_name__icontains=query)) | PlayLog.objects.filter(Q(Campaign_Name__icontains=query)) | PlayLog.objects.filter(Q(Display_Unit_Name__icontains=query)) | PlayLog.objects.filter(Q(Frame_Name__icontains=query))
    paginator = Paginator(context, 20)
    page_obj = paginator.get_page(page_number)
    return render(request, 'dashboard.html', {'page_obj': page_obj})

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value
def date_range_view(request):
    if request.method == 'POST':

        # PlayLog.objects.all().delete()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        action = request.POST.get('action')

        if not start_date or not end_date:
            # Handle case when start_date or end_date is empty
            return render(request, 'dashboard.html')

        # Convert start_date and end_date to datetime objects
        start_datetime = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(), time.min)
        end_datetime = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(), time.max)



        # Query the model using start and end dates
        page_obj = PlayLog.objects.filter(
            end_time__range=[start_datetime, end_datetime]
        ).select_related('campaign','player')

        query = request.POST.get('query', '')
        if action == 'search':
            if query:
                # Filter the page_obj based on the search query
                page_obj = page_obj.filter(
                    Q(campaign__name__icontains=query) & ~Q(campaign__name='')
                )

            # Create a Paginator object with the filtered page_obj
            paginator = Paginator(page_obj, 10)  # Adjust pagination size as needed

            page_number = request.POST.get('page', 1)

            # Retrieve the specified page from the paginator
            page_obj = paginator.get_page(page_number)

            count_data = page_obj.paginator.count  # Get the count of data

            return render(
                request,
                'dashboard.html',
                {
                    'page_obj': page_obj,
                    'query': query,
                    'count_data': count_data,
                    'start_date': start_date,
                    'end_date': end_date
                }
            )

        if action == 'export':
            """A view that streams a large CSV file."""
            # Generate a sequence of rows. The range is based on the maximum number of
            # rows that can be handled by a single sheet in most spreadsheet
            # applications.
            if query:
                # Filter the page_obj based on the search query
                page_obj = page_obj.filter(
                    Q(campaign__name__icontains=query) & ~Q(campaign__name='')
                )
            rows = [[item.player.name, item.end_time, item.duration, item.ad_copy_name, item.Number_of_Screens,
                   item.campaign.name, item.Frame_Name, item.Display_Unit_Name, item.Impressions,
                   item.Interactions, item.Extra_Data, item.variable] for item in page_obj]
            rows.insert(0,["Player Name","End Time","Duaration","Ad Copy Name","Number of Screens",
                           "Campaign Name","Frame Name","Display Unit Name","Impressions","Interactions","Extra Data",
                           "Variable"])
            pseudo_buffer = Echo()
            writer = csv.writer(pseudo_buffer)
            return StreamingHttpResponse(
                (writer.writerow(row) for row in rows),
                content_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="Exported_Data_{start_date}_to_{end_date}.csv"'},
            )


        if action == 'export_record':
            if query:
                # Filter the page_obj based on the search query
                page_obj = page_obj.filter(
                    Q(campaign__name__icontains=query) & ~Q(campaign__name='')
                )
            response = export_data_to_csv(page_obj,start_date,end_date)
            return response

    if request.method == 'GET':

        # PlayLog.objects.all().delete()
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')


        if not start_date or not end_date:
            # Handle case when start_date or end_date is empty
            return render(request, 'dashboard.html')

        # Convert start_date and end_date to datetime objects
        start_datetime = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(), time.min)
        end_datetime = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(), time.max)

        # Query the model using start and end dates
        page_obj = PlayLog.objects.filter(
            end_time__range=[start_datetime, end_datetime]
        ).select_related('campaign','player')

        query = request.GET.get('query', '')

        if query:
            # Filter the page_obj based on the search query
            page_obj = page_obj.filter(
                Q(campaign__name__icontains=query) & ~Q(campaign__name='')
            )

        # Create a Paginator object with the filtered page_obj
        paginator = Paginator(page_obj, 10)  # Adjust pagination size as needed

        page_number = request.GET.get('page', 1)

        # Retrieve the specified page from the paginator
        page_obj = paginator.get_page(page_number)

        count_data = page_obj.paginator.count  # Get the count of data

        return render(
            request,
            'dashboard.html',
            {
                'page_obj': page_obj,
                'query': query,
                'count_data': count_data,
                'start_date': start_date,
                'end_date': end_date
            }
        )




    return render(request, 'dashboard.html')



def export_csv(page_obj):
    pass


def export_data_to_csv(page_obj, start_date, end_date):
    campaign_data = (
        page_obj
        .exclude(campaign__name='')  # Exclude records with an empty Campaign Name
        .values('campaign__name')
        .annotate(rep=Count('campaign__name'), impressions=Sum('Impressions'))
    )
    print(campaign_data)
    data = [
        [
            start_date,
            end_date,
            campaign['campaign__name'],
            campaign['rep'],
            campaign['impressions']
        ]
        for campaign in campaign_data
    ]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="Exported_Report_{start_date}_to_{end_date}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Start_Date', 'End_Date', 'Campaign_Name', 'REP', 'IMP'])
    writer.writerows(data)

    return response

