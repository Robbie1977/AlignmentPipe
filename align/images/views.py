# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from images.models import Alignment
from django.views import generic

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
    record = Alignment.objects.get(id=image_id)
    chanCol = ['red','green','blue']
    for i in range(1,4):
      ax=fig.add_subplot(3,1,i)
      hist = dict(record.original_nrrd['Ch' + str(i) + '_pre_histogram'])
      k = [int(x) for x in hist.keys()]
      v = [int(y) for y in hist.values()]
      m = record.original_nrrd['Ch' + str(i) + '_new_boundary']['min']
      M = record.original_nrrd['Ch' + str(i) + '_new_boundary']['max']
      ax.broken_barh([(m, (M-m))] , (min(v), (max(v)-min(v))), facecolors='grey')
      ax.bar(k, v, color=chanCol[i-1], log=True)
      ax.set_xlim(0,260)
      ax.set_title('Ch' + str(i) + ' histogram', fontsize=14, color=chanCol[i-1])

    fig.text(0.5, 0.015, 'Intensity', ha='center', va='center')
    fig.text(0.015, 0.5, 'Count (log)', ha='center', va='center', rotation='vertical')
    fig.tight_layout()
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')

    canvas.print_png(response)
    return response

    image_type

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

    record = Alignment.objects.get(id=image_id)

    if '_file' in image_type:
      file = record.original_nrrd[image_type]
    elif 'temp_initial_nrrd' in image_type:
      file = record.temp_initial_nrrd
    elif 'aligned_BG' in image_type:
      file = record.aligned_BG
    elif 'aligned_SG' in image_type:
      file = record.aligned_SG
    elif 'aligned_AC1' in image_type:
      file = record.aligned_AC1
    else:
      file = 'default.png'
    if os.path.isfile(file):
      data, header = nrrd.read(file)
      data = np.max(data, axis=2)
      fig = Figure()
      ax=fig.add_subplot(1,1,1)
      imgplot = ax.imshow(data)
      imgplot.set_cmap('spectral')
      fig.colorbar(imgplot)
      ax.set_title(str(image_type).replace('temp_initial_nrrd', 'after initial alignment').replace('_',' ').replace('file', 'after preprocessing'), fontsize=14)

      canvas = FigureCanvas(fig)
      response = HttpResponse(content_type='image/png')

      canvas.print_png(response)
      return response
