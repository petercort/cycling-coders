from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound

from fitparse import FitFile
import pandas as pd
import numpy as np
import matplotlib
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
matplotlib.use("Agg")


def index(request):
  # This is a ugly hack
  # to avoid timing issues
  fitfile = FitFile('RideData/Pettit.fit')

  while True:
      try:
          fitfile.messages
          break
      except KeyError:
          continue

  # Get all data messages that are of type record
  workout = []
  for record in fitfile.get_messages('record'):
      r = {}
      # Go through all the data entries in this record
      for record_data in record:
          r[record_data.name] = record_data.value

      workout.append(r)

  df = pd.DataFrame(workout)
  df_dropped = df.drop(['distance', 'timestamp'], axis=1)
  means = df_dropped.mean()
  errors = df_dropped.std()
  fig, ax = plt.subplots()

  means.plot.bar(yerr=errors, ax=ax)

  fig, ax = plt.subplots()
  df[['power', 'heart_rate', 'cadence']].plot.hist(bins=100, alpha=0.5, range=(0, 400), ax=ax)
  ax.legend()
  # Customize the grid
  ax.set_axisbelow(True)
  ax.minorticks_on()
  ax.grid(which='major', linestyle='-', linewidth='0.5', color='red')
  ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')

  fig, ax = plt.subplots()
  df[['power', 'heart_rate', 'cadence']].plot(ax=ax)
  ax.legend()
  plt.xlabel("Seconds")
  # Customize the grid
  ax.set_axisbelow(True)
  ax.minorticks_on()
  ax.grid(which='major', linestyle='-', linewidth='0.5', color='red')
  ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')

  FigureCanvasAgg(fig)
  buf = io.BytesIO()
  plt.savefig(buf, format='png')
  plt.close(fig)
  response = HttpResponse(buf.getvalue(), content_type='image/png')
  return response