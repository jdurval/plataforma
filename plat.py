#!/usr/bin/env python
# coding: utf-8

# In[2]:


from ipywidgets import widgets
#from datetime import date
from matplotlib import dates 
import numpy as np
#warnings.filterwarnings('ignore')
import pandas as pd
from scipy.interpolate import griddata #, bisplrep, bisplev
import plotly.graph_objects as go
#import plotly.express as px


# In[47]:


par=['data', 'obs', 'perf', '_CntRS232', 'prof',
        'Temperatura', 'Condutividade', 'Oxigênio Dissolvido',
        'Saturacao de Oxigênio', 'Turbidez', 'pH', 'ORP', ' ', 'prof2']
paru=['', '', '' , ' ', '','°C', 'µS/cm', 'mg/L', '%', 'NTU', '',  'mV']
z=np.ndarray((25, 6621, 8))
def lest(es="Daphnia"):
    #est=west.value
    if  es=="Espirogira":
        arq="CR1000_I2_Espirogira_PFL_Step.dat";
    if  es=="Daphnia":
        arq='CR1000_I1_Daphnia_PFL_Step.dat'
    if  es=="Diatomacea":
        arq='CR1000_I3_Diatomacea_PFL_Step.dat'
      
    global z, est
    est=es
    dap=pd.read_csv(arq,skiprows=3)
    dap.columns=[u'data', u'obs', u'perf', u'dt', u'prof',
       u'temp', u'cond', u'OD',  u'ODsat', u'turb', u'pH',
       u'ORP', u' ', u'prof2']
    dap.dt=[dates.datestr2num(x) for x in dap.data]
    dap.data=pd.to_datetime(dap.data)
    dap=dap.set_index(pd.DatetimeIndex(dap.data))
    dap=dap.sort_index()
    #acrescenta perfil a partir das datas
    v=[]        
    for i in range(dap.shape[0]-1):
        if i==0:
            dtp=dap.dt.iloc[i]
            v.append(dtp)
        if dap.perf.iloc[i]!=dap.perf.iloc[i+1]:
            dtp=dap.dt.iloc[i+1]
        v.append(dtp)
    dap['v']=v
    
    #trata dados
    
    #if est.find('Dia')>-1:
    #    dap=dap['2021-06'::] 
        
    dap=dap.set_index(pd.DatetimeIndex(dap.data))
    dap=dap.sort_index()
    dap.perf=dap.perf-min(dap.perf)
    dap.prof=dap.prof.astype('float64')
    dap.temp=dap.temp.astype('float64')
    dap[dap.prof<=0.1]=np.nan
    dap=dap[~np.isnan(dap.prof)]
    dap.temp[dap.temp<10]=np.nan
    dap.pH[dap.pH<4]=np.nan
    #dap.turb[dap.turb>500]=np.nan
    dap.turb[dap.turb<0]=np.nan
   
    x=pd.date_range(dates.num2date(round(dap.v[0],ndigits=1)),dates.num2date(round(dap.v[-1],ndigits=1)),freq='3H')
    x=dates.date2num(x)
    prof=np.arange(round(min(dap.prof),1)-.3,round(max(dap.prof)+.3,1),.5)
    X, Y = np.meshgrid(x, prof)
    z=np.ndarray(shape=(np.shape(Y)[0],np.shape(Y)[1],8))
    pmax=dap.prof.groupby(by=dap.v, axis=0).max()
    pmax=pmax* -1
    from scipy.signal import savgol_filter
    pmax = savgol_filter(pmax, 5, 1)
    pmax=np.interp(X[1,:],np.unique(dap.v),pmax)         
    #corta periodos faltantes
    dif=np.diff(dap.data)*2.77777777778  * 10e-13
    dif=pd.DataFrame(pd.to_numeric(dif))
    dif=dif[dif>60].dropna()
    parada=pd.DataFrame()
    parada['dind'] = [d for d in dif.index]
    parada['dinicio'] = [dap.data[d] for d in dif.index]
    parada['dfim'] = [dap.data[d+1] for d in dif.index]
    parada['periodo'] = [dap.data[d+1]-dap.data[d] for d in dif.index]

    for k in range (5,12):
        zi=griddata((dap.v,dap.prof), dap.iloc[:,k], (X,Y), method="nearest")#,fill_value=np.nan)
        for i in np.arange(np.shape(zi)[1]):
            zi[prof>pmax[i]*-1,i]=np.nan

        for i in np.arange(0,parada.shape[0]):
            zi[:,X[1,:].searchsorted(dates.date2num((parada.dinicio[i]))):X[1,:].searchsorted(dates.date2num((parada.dfim[i])))]=np.nan
        #
        z[:,:,k-5]=zi
        if k==5:
            fig = go.FigureWidget(data=[go.Contour(z=zi,x=dates.num2date(x),y=prof*-1,line_width=0,colorscale='Jet',reversescale=False,contours_coloring='heatmap' )])
            fig.update_layout(title= '        ' + est + '    -     '+par[k]+ '  '+ paru[k] , autosize=False, 
                width=1200, height=600, yaxis_title="profundidade (m)",
                margin=dict(l=65, r=50, b=65, t=65))   
    return z, fig, est

 #  funcao gera grafico : k=parametro dap=dap   
def graf(k=5,zi=z):
    global z, est
    #k=wpar.index+5
    zi=z[:,:,k-5]
    #fig = go.FigureWidget(data=data,y=prof*-1,line_width=0,colorscale='Jet',reversescale=False,contours_coloring='heatmap' ])
    with fig.batch_update():
        fig.data[0].z = zi
        fig.layout.title= title= '        ' + est + '    -     '+par[k]+ '  '+ paru[k] 
    if 6<k<9:
        fig.update_traces(reversescale=True)
      #print (par[k], ' cor invertida')
    
    return fig



 # Acessa os dados das plataformas e salva no diretório atual

#baixa()
#from google.colab import drive
#drive.mount('/content/drive')

import ftplib
def baixa():
    ftp = ftplib.FTP('ftp.itaipu.gov.br', 'svcqualidadedeagua','#QDagua@2020!')
    files = ftp.nlst()
    for file in files:
        #print("Buscando arquivos da estação..." + file)
        ftp.retrbinary("RETR " + file ,open(file, 'wb').write)
    ftp.close()


#gera todos os parametros 
def exportest(l):
    dir='/content/drive/MyDrive/graficos_plataformas/'
    dir = '~/Downloads/'
    par=['data', 'obs', 'perf', '_CntRS232', 'prof',
    'Temperatura', 'Condutividade', 'Oxigênio Dissolvido',
    'Saturacao de Oxigênio %', 'Turbidez', 'pH', 'ORP', ' ', 'prof2']
    #est=west.value
    for k in range (5,12):
        #print(par[k])
        fig=graf(k)
        name=str(np.char.add(est+'-'+par[k]+'-pl-',str( fig.data[0].x[-1])[0:10]+".html"))
        fig.write_html(name)
        
def response(change):
        k=wpar.index+5 
        global z,est
        #est=west.value
        #dat=[go.Contour(z=zi,x=dates.num2date(x),y=prof*-1 )]
        #
        #              width=1200, height=600, yaxis_title="profundidade (m)",
        #              margin=dict(l=65, r=50, b=65, t=65))
        #z,fig, est =lest(west.value);   
        zi=z[:,:,k-5]   
        with fig.batch_update():
            fig.data[0].z = zi
            fig.layout.title= par[k]+ '  '+ paru[k] +'    -     ' + est 
        #z,fig, est =lest(west.value); 
        
            
def renova(change):
    k=wpar.index+5
    global z,est
    est=west.value
   
    z,fig, est =lest(est); 
    
    #fig= graf(k,z)
    with fig.batch_update():
         fig.layout.title= par[k]+ '  '+ paru[k] +'    -     ' + est 
    return  z,fig, est
    


# In[ ]:





# In[5]:



##fig=graf(wpar.index+5,z)
#est=west.value
wpar= widgets.Dropdown( options= ['Temperatura', 'Condutividade', 'Oxigênio Dissolvido',
                'Saturacao de Oxigênio %', 'Turbidez', 'pH', 'ORP'])    
west=widgets.Dropdown( options=['Espirogira', 'Daphnia', 'Diatomacea'])
z, fig, est =lest(west.value);
wsave=widgets.Button(description='Salva')
container = widgets.HBox(children=[wpar, west, wsave])
wsave.on_click(exportest)
wpar.observe(response, names="value")
west.observe(renova, names="value")
widgets.VBox([container,fig])


# In[14]:


#exportest(7)


# In[ ]:



from ipywidgets import interact
#interact(graf, k=[5,6,7,8]);


# In[1]:





# In[75]:


#fig.data[0].zmax=10
#colorscale[3:][0:2]
                                ##fig.data[0].zmax=10
#fig.data[0].autocolorscale=True


# In[78]:



#fig.update_layout()


# In[ ]:




