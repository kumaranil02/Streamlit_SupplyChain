import pandas as pd
import streamlit as st
import itertools
import pandas as pd
import gurobipy as gp
from gurobipy import GRB


st.title("Supply Network Design")

from PIL import Image
image = Image.open('IMT.jpg')

st.image(image)

supply = st.text_input('Please enter supply locations - separated by "," ','P1,P2')
st.write('The supply locations entered are',supply)

sd = {}
for i in supply.split(','):
  sd[i] = st.number_input("Enter Capacity for " + i,0,100000000,500000,1)	
  st.write(sd[i])

through = st.text_input('Please enter through routes - separated by "," ','D1,D2,D3,D4')
st.write('The through routes entered are',through)

td = {}
for i in through.split(','):
  td[i] = st.number_input("Enter Capacity for " + i,0,100000000,500000,1)	
  st.write(td[i])

destinations = st.text_input('Please enter destinations - separated by "," ','A1,A2,A3,A4,A5,A6')	
st.write('The supply locations are',destinations)

dd = {}
for i in destinations.split(','):
  dd[i] = st.number_input("Enter Demand for " + i,0,100000000,500000,1)	
  st.write(dd[i])

a = [supply.split(',') ,through.split(',')]
b = [through.split(','),destinations.split(',')]
c = [supply.split(',') ,destinations.split(',')]	
a1 = list(itertools.product(*a))
b1 = list(itertools.product(*b))
c1 = list(itertools.product(*c))

a1.extend(b1)
a1.extend(c1)

ad = {}
for i in a1:
  ad[i] = st.slider('Enter shipping cost for '+ str(i), 0, 5000, 750)	
  st.write(ad[i])


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

st.write("The Suggested Optimizations are:")

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
      edge_label_fontdict=dict(size=12),
      edge_layout='straight',node_size=4, edge_width=2, arrows=True)

#st.set_option('deprecation.showPyplotGlobalUse', False)
st.write("The Suggested Optimized Costs are ")

st.pyplot()
#plt.show()

image = Image.open('scm.jpg')

st.image(image)
