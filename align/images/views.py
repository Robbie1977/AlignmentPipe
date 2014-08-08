# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from images.models import Alignment, Original_nrrd, comp_orien, conv_orien, Upload
from system.models import Setting, Server, Template
from django.views import generic
from socket import gethostname
from django.db.models import Q
from django.contrib.auth.models import User

from images.forms import UploadForm

host = gethostname()

tempfolder = str(Server.objects.filter(host_name=host).values('temp_dir')[0]['temp_dir'])
uploaddir = str(Server.objects.filter(host_name=host).values('upload_dir')[0]['upload_dir'])

def index(request):
    if not request.user == '':
      cu = int(User.objects.filter(username=request.user).values('id')[0]['id'])
      if cu == 1:
        align_list = Alignment.objects.order_by('alignment_stage', 'name')
        context = {'align_list': align_list}
      else:
        if Alignment.objects.filter(Q(user=cu) | Q(user=0)).count() > 0:
          align_list = Alignment.objects.filter(Q(user=cu) | Q(user=0)).order_by('alignment_stage', 'name')
          context = {'align_list': align_list}
        else:
          context = {}
      return render(request, 'index.html', context)
    else:
      return HttpResponseRedirect('/admin')

def detail(request, image_id):
    if not request.user == '':
      align_list = Alignment.objects.get(id=image_id)
      context = {'record': align_list}
      return render(request, 'details.html', context)
    else:
      return HttpResponseRedirect('/admin')

def handle_uploaded_file(ufile, dest):
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    path = default_storage.save(dest, ContentFile(ufile.read()))
    return path
    #
    # dest = open(dest, 'wb+')
    # dest.write(ufile)
    # dest.close()


def upload(request):
    from django.contrib import messages
    from django.conf import settings as st
    import os, stat, sys
    # Handle file upload
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = str(request.user) + '-' + str(request.FILES['file'])
            setting = Setting.objects.get(id=int(request.POST['settings']))
            if '.tif' in file or '.lsm' in file:
              # file = str(st.MEDIA_URL) + file
              file = handle_uploaded_file(request.FILES['file'], dest=file)
              name = str(os.path.splitext(os.path.basename(file))[0])
              ext = str(os.path.splitext(os.path.basename(file))[1])
              folder = str(st.MEDIA_ROOT)
              ori = str(request.POST['orientation'])
              cu = User.objects.get(username=request.user)
              newimage = Alignment(name=name, orig_orientation=ori, settings=setting, original_path=folder, original_ext=ext, alignment_stage=1, last_host=host, loading_host=host, user=cu)
              newimage.save()
              os.chmod(folder + file, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
              return HttpResponseRedirect('/admin')
            else:
              messages.error(request, 'Not a LSM or tif file')
              return HttpResponseRedirect('/admin')
        # else:
        # messages.error(request, 'Invalid data')
    else:
        form = UploadForm() # A empty, unbound form

    # Render list page with the documents and the form
    align_list = Alignment.objects.all().order_by('alignment_stage', 'name')
    context = {'align_list': align_list, 'form': form}
    return render_to_response('index.html', context, context_instance=RequestContext(request))


# def showStaticImage(request):
#     """ Simply return a static image as a png """
#     imagePath = "images/default.png"
#     from PIL import Image
#     Image.init()
#     i = Image.open(imagePath)
#     response = HttpResponse(mimetype='image/png')
#     i.save(response,'PNG')
#     return response

def plotResults(request, image_id):
    import os
    import tempfile
    os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
    import matplotlib
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    import numpy as np
    fig = Figure()
    ax=fig.add_subplot(3,1,1)
    if Original_nrrd.objects.filter(image=image_id).count() > 0:
      records = Original_nrrd.objects.filter(image=image_id).values()
      chanCol = ['red','green','blue']
      for record in records:
        i = int(record['channel'])
        ax=fig.add_subplot(3,1,i)
        hist = list(record['pre_hist'])
        k = range(0,len(hist))
        v = [long(y) for y in hist]
        m = int(record['new_min'])
        M = int(record['new_max'])
        ax.fill([m,M,M,m], [np.min(v),np.min(v),np.max(v),np.max(v)], 'cyan', fill=True, hatch='/', edgecolor="grey")
        # ax.broken_barh([(m, (M-m))] , (ax.yaxis, (np.max(v)-np.min(v))), facecolors='grey')
        ax.bar(k, v, color=chanCol[i-1])#, log=True

        ax.set_xlim(0,260)
        ax.set_ylim(0,np.max(v))
        ax.set_yscale('symlog', linthreshx=np.average(v))
        ax.grid(True)

        ax.set_title('Ch' + str(i) + ' histogram', fontsize=14, color=chanCol[i-1])
    else:
      fig.text(0.3,0.5,'No Data Found!', fontsize=32)
    fig.text(0.5, 0.015, 'Intensity', ha='center', va='center')
    fig.text(0.015, 0.5, 'Count (log)', ha='center', va='center', rotation='vertical')
    fig.tight_layout()
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')

    canvas.print_png(response)
    return response

    image_type

def opositeOr(position):
    Or = {'R':'L','L':'R','P':'A','A':'P','S':'I','I':'S'}
    return Or[position]

def plotNrrd(request, image_id, image_type):
    import os
    import matplotlib
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    import nrrd
    import numpy as np
    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt
    from system.models import checkDir, Server

    record = checkDir(Alignment.objects.get(id=image_id))

    file = 'default.png'
    subtext = ''
    orient = 'LPS'
    fsize = 18
    if '_file' in image_type:
      if Original_nrrd.objects.filter(image=image_id, channel=int(image_type.replace('Ch','').replace('_file',''))).count() > 0:
        temprec = Original_nrrd.objects.get(image=image_id, channel=int(image_type.replace('Ch','').replace('_file','')))
        file = tempfolder + str(temprec.file)
        del temprec
        orient = str(record.settings.template.orientation)
        subtext = 'Orientation: ' + str(comp_orien[str(record.settings.template.orientation)]) + ' (' + orient + ')'
    elif 'temp_initial_nrrd' in image_type:
      file = tempfolder + str(record.temp_initial_nrrd)
      orient = str(record.settings.template.orientation)
      subtext = 'Orientation: ' + str(record.orig_orientation) + ' (' + orient + ')'
    elif 'aligned_bg' in image_type:
      file = tempfolder + str(record.aligned_bg)
      orient = str(record.settings.template.orientation)
      subtext = 'Orientation: ' + str(comp_orien[str(record.settings.template.orientation)]) + ' (' + orient + ')'
    elif 'aligned_sg' in image_type:
      file = tempfolder + str(record.aligned_sg)
      orient = str(record.settings.template.orientation)
      subtext = 'Orientation: ' + str(comp_orien[str(record.settings.template.orientation)]) + ' (' + orient + ')'
    elif 'aligned_ac1' in image_type:
      file = tempfolder + str(record.aligned_ac1)
      orient = str(record.settings.template.orientation)
      subtext = 'Orientation: ' + str(comp_orien[str(record.settings.template.orientation)]) + ' (' + orient + ')'
    elif 'template' in image_type:
      temprec = Server.objects.get(host_name=host)
      file = str(temprec.template_dir) + str(record.settings.template.file)
      orient = str(record.settings.template.orientation)
      subtext = 'Orientation: ' + str(comp_orien[str(record.settings.template.orientation)]) + ' (' + orient + ')'
      del temprec
      fsize = 12
    else:
      file = 'default.png'
    if os.path.isfile(file):
      ori = list(orient)
      data, header = nrrd.read(file)
      data = data.swapaxes(0,1)
      zdata = np.max(data, axis=2)
      xdata = np.max(data, axis=1)
      del data
      fig = Figure()
      ax=fig.add_subplot(1,2,1)
      imgplot = ax.imshow(xdata)
      imgplot.set_cmap('spectral')
      ax.set_title('Max proj. (X)')
      ax.set_xlabel('Z [' + str(opositeOr(ori[2])) + '->' + str(ori[2]) + '] (Px)', fontsize=10)
      ax.set_ylabel('Y [' + str(ori[1]) + '<-' + str(opositeOr(ori[1])) + '] (Px)')
      ax.yaxis.set_ticks(np.round(np.linspace(ax.get_ylim()[0],ax.get_ylim()[1],3)))
      ax.xaxis.set_ticks(np.round(np.linspace(ax.get_xlim()[0],ax.get_xlim()[1],3)))
      ax=fig.add_subplot(1,2,2)
      imgplot = ax.imshow(zdata)
      imgplot.set_cmap('spectral')
      fig.colorbar(imgplot, ax=ax, aspect=7.5)
      del xdata, zdata
      fig.suptitle(str(image_type).replace('temp_initial_nrrd', 'after initial alignment').replace('_',' ').replace('file', 'after preprocessing').title().replace('Template',str(record.settings.template)).replace('Bg','Background').replace('Sg','Signal').replace('Ac1','Additional Channel 1'), fontsize=fsize)
      ax.set_title('Max proj. (Z)')
      ax.set_xlabel('X [' + str(opositeOr(ori[0])) + '->' + str(ori[0]) + '] (Px)')
      ax.set_ylabel('Y [' + str(ori[1]) + '<-' + str(opositeOr(ori[1])) + '] (Px)')
      ax.yaxis.set_ticks(np.round(np.linspace(ax.get_ylim()[0],ax.get_ylim()[1],3)))
      ax.xaxis.set_ticks(np.round(np.linspace(ax.get_xlim()[0],ax.get_xlim()[1],3)))
      fig.text(0.3,0.005,subtext)
      # fig.tight_layout()
      canvas = FigureCanvas(fig)
      response = HttpResponse(content_type='image/png')

      canvas.print_png(response)
      return response
    else:
      fig = Figure()
      canvas = FigureCanvas(fig)
      ax=fig.add_subplot(1,1,1)
      ax.set_title('No Image')
      ax.set_xlabel(file, fontsize=8)
      fig.text(0.3,0.5,'No Data Found!', fontsize=32)
      response = HttpResponse(content_type='image/png')
      canvas.print_png(response)
      return response
