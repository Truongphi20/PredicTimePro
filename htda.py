import pandas as pd
import networkx as nx
import math 
import scipy.stats as stats
import argparse

def tim_vector(tenda,pretenda): # Tim cac vector tren giang do
	Start_point = [i for i in tenda if pretenda[tenda.index(i)] == '-'] #Tìm start point
	#print(Start_point)

	# Liệt kê các vector:
	##Thêm vector start point
	vector = [["Start",i] for i in Start_point] 
	#print(vector)

	##Thêm vector trung gian
	for i in range(len(pretenda)): 
	    if pretenda[i] != "-" and len(pretenda[i]) == 1:
	        vector.append([pretenda[i],tenda[i]])
	    elif len(pretenda[i]) > 1:
	        Stats = pretenda[i].split(",")
	        for k in range(len(Stats)):
	            vector.append([Stats[k],tenda[i]]) 
	#print(vector)

	##Tìm end point
	End_point = []
	for i in range(len(tenda)):
	    a = 0
	    for k in range(len(pretenda)):
	        if tenda[i] in pretenda[k]:
	            a += 1
	    if a == 0:
	        End_point.append(tenda[i])
	#print(End_point)

	vector.extend([[i,'End'] for i in End_point])
	#print(vector)
	return vector

def all_paths(G): # Xuat ra cac con duong
    roots = (v for v, d in G.in_degree() if d == 0)
    leaves = [v for v, d in G.out_degree() if d == 0]
    all_paths = []
    for root in roots:
        paths = nx.all_simple_paths(G, root, leaves)
        all_paths.extend(paths)
    return all_paths

def pathsf(tenda,pretenda): # Xac dinh cac con duong
	# Xac dinh cac con duong
	## Xac dinh cac vecto
	vector = tim_vector(tenda,pretenda)
	#print(vector)
	## Xac dinh cac con duong
	G = nx.DiGraph()
	G.add_edges_from(vector)
	paths = all_paths(G)
	#print(lisotoString(paths))
	return paths

# Tạo hàm tính EST và EFT
def Find_pp(paths,nameac): # Tim cac diem lien ke truoc cua 1 diem tron cac con duong
    beforeac = [sublist[i-1] for sublist in paths for i in range(len(sublist)) if sublist[i] == nameac] # Lay cac ac nam truoc nameac trong cac con duong
    #print(beforeac)
    beforeac_uniq = []
    tem = [beforeac_uniq.append(i) for i in beforeac if i not in beforeac_uniq] # Chon loc duy nhat
    #print(beforeac_uniq)
    return beforeac_uniq
#print(Find_pp(paths,nameac))

def Find_est(tenac,te_vals,paths): # Tìm est vaf eft cua cac cong viec
    est_lib = {tenac[i]:[0,te_vals[i]] for i in range(len(tenac))} # Tao thu vien est
    #print(est_lib)

    for path in paths:
        for i in range(2,len(path)-1): # Tinh cac 1 input truoc
            pp = Find_pp(paths,path[i])
            #print(pp)
            if len(pp) == 1:
                est_lib[path[i]][0] = est_lib[pp[0]][0]+est_lib[pp[0]][1]
        
        for i in range(2,len(path)-1): # Tinh cac hai input tro len
            pp = Find_pp(paths,path[i])
            #print(pp)
            if len(pp) > 1:
                est_lib[path[i]][0] = max([est_lib[k][0]+est_lib[k][1] for k in pp])
        
        for i in range(2,len(path)-1): # Tinh lai cac 1 input
            pp = Find_pp(paths,path[i])
            #print(pp)
            if len(pp) == 1:
                est_lib[path[i]][0] = est_lib[pp[0]][0]+est_lib[pp[0]][1]

    #print(est_lib)
    est_vals = [est_lib[i][0] for i in est_lib]
    eft_vals = [sum(est_lib[i]) for i in est_lib]
    #print(est_vals)
    return est_vals, eft_vals

def Tim_gantt(paths,tenda,tg1): # Rà thời gian thực hiện dự án của các con đường 
    g_list = []
    for i in range(len(paths)):
        g_val = []
        for k in range(1,len(paths[i])-1):
            for j in range(len(tenda)):
                if tenda[j] == paths[i][k]:
                    g_val.append(tg1[j])
        g_list.append(g_val)
    return g_list

class Ganttc(): 
	def __init__(self,tenda,paths,tg1):
		self.tenda = tenda
		self.paths = paths
		self.tg1 = tg1
		self.g_list = Tim_gantt(self.paths,self.tenda,self.tg1)
    #print(g_list)

	def time(self): # Tra ve thoi gian hoan thanh du an    
		return [sum(i) for i in self.g_list]
    	#print("Thời gian hoàn thành: "+ str(g_val_list))

	def gantt(self): # Tra ve duong gantt
	    max_tg = max(self.time())
	    #print(max_tg)

	    Gantt = [self.time().index(max_tg)]
	    return Gantt

def Xacsuat(data,time): #Tinh xac xuat hoan thanh du an
	tenac = list(data.iloc[:,0]) # ten du an
	prede = list(data.iloc[:,1]) #ten du an truoc
	te_vals = list(data.iloc[:,2]) # gia tri te
	ps = list(data.iloc[:,3]) # phuong sai


	paths =  pathsf(tenac,prede) # Cac con duong
	est_vals, eft_vals = Find_est(tenac,te_vals,paths)
	time_end = eft_vals[-1] # thoi gian ket thuc du an

	Gantt = Ganttc(tenac,paths,te_vals)

	te_paths = Gantt.time()
	#print(te_paths)

	index_gantt = Gantt.gantt()
	#print(index_gantt)

	# Tính tổng sigma trên đường Gantt
	#print(paths[index_gantt[0]])
	index_lay = [i for i in range(len(tenac)) if tenac[i] in paths[index_gantt[0]]] # lay index tren Gantt 
	#print(index_lay)

	sum_sig = sum([ps[i] for i in index_lay])
	#print("Gia tri tong sigma tren Gantt: "+str(sum_sig)) 

	## Tính độ lệch chuẩn
	sigma = math.sqrt(sum_sig)

	# Chuyển sang phân bố Z
	time_z = (time - time_end)/sigma
	#print(time_z) 
	ss = stats.norm.cdf(time_z)
	print(f'Xác suất hoàn thanh dự án là: {round(ss*100,2)}%')
	return ss


# Initialize parser
parser = argparse.ArgumentParser()

parser.add_argument("-f", "--input_file")
parser.add_argument("-d", "--day")
parser.add_argument("-v",'--version', action='version', version='%(prog)s 1.0',help = 'show version')

# Read arguments from command line
args = parser.parse_args()
data = pd.read_csv(args.input_file, sep = "\t")
#print(data)
time  = int(args.day)

Xacsuat(data,time)





