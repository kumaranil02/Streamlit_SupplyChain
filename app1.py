import warnings
import pandas as pd
import streamlit as st
from streamlit_tags import st_tags
import itertools
import pandas as pd
import gurobipy as gp
from PIL import Image
from gurobipy import GRB
import base64
st.set_option('deprecation.showPyplotGlobalUse', False)
warnings.simplefilter('ignore')
pd.set_option('display.float_format', lambda x: '%.5f' % x)
pd.set_option('display.max_columns', None)

st.set_page_config(
    layout='wide',  page_title='Supply Chain Network Design', page_icon='🚚')


# [theme]
# primaryColor = "#285a21"
# backgroundColor = "#a5b9b6"
# secondaryBackgroundColor = "#e6e4e4"
# textColor = "#1e4845"
# font = "serif"


def set_bg_hack(main_bg):
    st.set_option('deprecation.showPyplotGlobalUse', False)
    main_bg_ext = "png"
    st.markdown(
        f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
        unsafe_allow_html=True
    )


#set_bg_hack('t1.jpg')


st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 220px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 280px;
        margin-left: -260px;
    }
    </style>
    """,
    unsafe_allow_html=True,)

st.image(Image.open('n1.jpg'))

# r1,r2= st.columns([4,2])
# with r1:
#   st.title("Supply Network Design")
  
# with r2:
#   st.image(Image.open('t1.jpg'))



im = Image.open('scm.jpg')
st.write("")




image = Image.open('IMT.jpg')

st.sidebar.image(image)
st.sidebar.markdown("### Developed by:\n #   **Sunil Kumar** \n ### Roll -200301014")
st.sidebar.image(Image.open('pic.jpg'))
st.sidebar.write("")
st.sidebar.image(Image.open('pic 2.png'))
c1,c2,c3 = st.columns(3)

#st.write('The supply locations entered are',supply)
with st.container():
  with c1:
    supply = st_tags(label='##### Please Enter Supply locations',
                    text='Press enter to add more',
                    value=['P1', 'P2'])
    sd = {}
    for i in supply:
      sd[i] = st.number_input("Enter Capacity for " + i,0,100000000,500000,1)   
      #st.write(sd[i])

with st.container():
  with c2:
    through = st_tags(label='##### Please Enter Through Routes',
                      text='Press enter to add more',
                      value=['D1', 'D2', 'D3', 'D4'])
    td = {}
    for i in through:
      td[i] = st.number_input("Enter Capacity for " + i,0,100000000,500000,1)   
      #st.write(td[i])
      
with st.container():
  with c3:
    destinations = st_tags(label='##### Please Enter Destinations',
                          text='Press enter to add more',
                          value=['A1', 'A2', 'A3', 'A4', 'A5', 'A6'])
    dd = {}
    for i in destinations:
      dd[i] = st.number_input("Enter Demand for " + i,0,100000000,500000,1) 
      #st.write(dd[i])

a = [supply ,through]
b = [through,destinations]
c = [supply ,destinations]    
a1 = list(itertools.product(*a))
b1 = list(itertools.product(*b))
c1 = list(itertools.product(*c))


#a1.extend(b1)
#a1.extend(c1)
k1, k2, k3 = st.columns(3)

with k1:
  ad1 = {}
  for i1 in a1:
    ad1[i1] = st.slider('Enter shipping cost for '+ str(i1), 0, 5000, 750)   
    #st.write(ad1[i1])

with k2:
  ad2 = {}
  for i2 in b1:
    ad2[i2] = st.slider('Enter shipping cost for ' + str(i2), 0, 5000, 750)
    #st.write(ad2[i2])


with k3:
  ad3 = {}
  for i3 in c1:
    ad3[i3] = st.slider('Enter shipping cost for ' + str(i3), 0, 5000, 750)
    #st.write(ad3[i3])


def Merge(dict1, dict2,dict3):
    res = {**dict1, **dict2,**dict3}
    return res
  
ad=Merge(ad1,ad2,ad3)

# Create dictionaries to capture factory supply limits, depot throughput limits, and customer demand.

supply = sd
through = td

demand = dd

# Create a dictionary to capture shipping costs.

arcs, cost = gp.multidict(ad)

model = gp.Model('SupplyNetworkDesign')
flow = model.addVars(arcs, obj=cost, name="flow")

factories = supply.keys()
factory_flow = model.addConstrs((gp.quicksum(flow.select(factory, '*')) <= supply[factory]
                                 for factory in factories), name="factory")

customers = demand.keys()
customer_flow = model.addConstrs((gp.quicksum(flow.select('*', customer)) == demand[customer]
                                  for customer in customers), name="customer")

depots = through.keys()
depot_flow = model.addConstrs((gp.quicksum(flow.select(depot, '*')) == gp.quicksum(flow.select('*', depot))
                               for depot in depots), name="depot")

depot_capacity = model.addConstrs((gp.quicksum(flow.select('*', depot)) <= through[depot]
                                   for depot in depots), name="depot_capacity")


model.optimize()

product_flow = pd.DataFrame(columns=["From", "To", "Flow"])
for arc in arcs:
  if flow[arc].x > 1e-6:
    product_flow = product_flow.append({"From": arc[0], "To": arc[1], "Flow": flow[arc].x}, ignore_index=True)  
product_flow.index=[''] * len(product_flow)

st.subheader("The Suggested Optimizations are:")

st.write(product_flow)


import networkx as nx
G = nx.Graph()


G = nx.from_pandas_edgelist(product_flow, 'From', 'To','Flow')

edge_labels = dict([((n1, n2),d['Flow'])
                    for n1, n2, d in G.edges(data=True)])

from matplotlib import pyplot as plt
from netgraph import Graph
plt.figure(figsize=(10, 10))

Graph(G, node_labels=True,edge_labels=edge_labels,
      edge_label_fontdict=dict(size=9),
      edge_layout='straight',node_size=3, edge_width=1.6, arrows=True)

#st.set_option('deprecation.showPyplotGlobalUse', False)
st.subheader("The Suggested Optimized Costs are ")

st.pyplot(figsize=(5, 5))
#plt.show()
st.write("")
l1,l2,l3= st.columns([1,2,1])


  
with l2:
  st.image(Image.open('thank.jpg'))



