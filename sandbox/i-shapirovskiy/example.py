from vpython import *  
import graphstore as g  

colIrr=color.orange;
colRefl=color.white;
colEdge=color.white;
colArr=color.orange; 

#draw nodes: 
for node in g.graph:
    coord=g.positions3d[node]
    v=vector(coord[0],coord[1],coord[2]) 
    #refl/irrefl:
    if ((node,node) in g.graph.edges): col=colRefl; op=0.5
    else:  col=colIrr; op=1
    points(pos=[v], color=col, opacity=op)     
    #simple_sphere(pos=v, radius=0.025, color=col, opacity=op)    
 
     
#draw edges: 
for edge in g.graph.edges:
    if (edge[0]!=edge[1]):
        coordA=g.positions3d[edge[0]];  coordB=g.positions3d[edge[1]]
        vA=vector(coordA[0],coordA[1],coordA[2]); vB=vector(coordB[0],coordB[1],coordB[2])  
        curve(pos=[vA,vB], color=colEdge)  
        vD=vB-vA
        ax=0.5*vD
        arrow(pos=vA+0.5*vD, axis=ax, color=colArr, shaftwidth=0.000001, headwidth=0.075, headlength=mag(vD)/3, round=True, 
              opacity=0.5)  
        #cone(pos=pos, axis=ax, color=colArr,   radius=0.02) 
   
#post-fix 
input("Press any key to exit")