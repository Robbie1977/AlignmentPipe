# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from images.models import Alignment, Original_nrrd, comp_orien, conv_orien
from system.models import Setting, Server, Template
from django.views import generic
from socket import gethostname

host = gethostname()

def index(request):
    align_list = Alignment.objects.all().order_by('name')
    context = {'align_list': align_list}
    return render(request, 'index.html', context)

def detail(request, image_id):
    align_list = Alignment.objects.get(id=image_id)
    context = {'record': align_list}
    return render(request, 'details.html', context)

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
    import matplotlib
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    fig = Figure()
    ax=fig.add_subplot(3,1,1)
    if Original_nrrd.objects.filter(image=image_id).count() > 0:
      records = Original_nrrd.objects.get(image=image_id)
      chanCol = ['red','green','blue']
      for record in records:
        i = int(record['channel'])
        ax=fig.add_subplot(3,1,i)
        hist = list(record['pre_hist'])
        k = range(1,len(hist))
        v = [int(y) for y in hist]
        m = record['new_min']
        M = record['new_max']
        ax.broken_barh([(m, (M-m))] , (min(v), (max(v)-min(v))), facecolors='grey')
        ax.bar(k, v, color=chanCol[i-1], log=True)
        ax.set_xlim(0,260)
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

    subtext = ''
    orient = 'LPS'
    if '_file' in image_type:
      temprec = Original_nrrd.objects.get(image=image_id, channel=int(image_type.replace('Ch','').replace('_file','')))
      file = temprec['file']
      del temprec
      orient = str(record.settings.template.orientation)
      subtext = 'Orientation: ' + str(comp_orien[str(record.settings.template.orientation)]) + ' (' + orient + ')'
    elif 'temp_initial_nrrd' in image_type:
      file = record.temp_initial_nrrd
      orient = conv_orien[str(record.orientation)]
      subtext = 'Orientation: ' + str(record.orientation) + ' (' + orient + ')'
    elif 'aligned_bg' in image_type:
      file = record.aligned_BG
      orient = str(record.settings.template.orientation)
      subtext = 'Orientation: ' + str(comp_orien[str(record.settings.template.orientation)]) + ' (' + orient + ')'
    elif 'aligned_sg' in image_type:
      file = record.aligned_SG
      orient = str(record.settings.template.orientation)
      subtext = 'Orientation: ' + str(comp_orien[str(record.settings.template.orientation)]) + ' (' + orient + ')'
    elif 'aligned_ac1' in image_type:
      file = record.aligned_AC1
      orient = str(record.settings.template.orientation)
      subtext = 'Orientation: ' + str(comp_orien[str(record.settings.template.orientation)]) + ' (' + orient + ')'
    elif 'template' in image_type:
      temprec = Server.objects.get(host_name=host)
      file = str(temprec.template_dir) + str(record.settings.template.file)
      orient = str(record.settings.template.orientation)
      subtext = 'Orientation: ' + str(comp_orien[str(record.settings.template.orientation)]) + ' (' + orient + ')'
      del temprec
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
      fig.colorbar(imgplot)
      del xdata, zdata
      fig.suptitle(str(image_type).replace('temp_initial_nrrd', 'after initial alignment').replace('_',' ').replace('file', 'after preprocessing').title(), fontsize=18)
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
      response = HttpResponse(content_type='image/png')
      canvas.print_png(response)
      return response
