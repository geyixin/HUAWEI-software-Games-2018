# -*- coding: UTF-8 -*-

__author__ = 'gyx & wmf'

import time
import datetime

def predict_vm(ecs_lines, input_lines):
    # Do your work from here#
    result = []
    if ecs_lines is None:
        print 'ecs information is none'
        return result
    if input_lines is None:
        print 'input file information is none'
        return result

    cpu_scale, mem_scale, kind_yuce, day_span, flavor_scale = read_input_data(input_lines)

    flavor_old_num,flavor_k = read_train_data_accordingTo_input_data(ecs_lines,flavor_scale)

    int_flavor_num_predict,result = num_yuce(result,flavor_old_num,day_span,flavor_k)

    result = put_virtual_machine(result,kind_yuce,cpu_scale,mem_scale,int_flavor_num_predict,flavor_k,flavor_scale)
    #print result
    return result

def read_input_data(input_lines):
    j=0
    flavor_scale=[]
    length=len(input_lines)

    for item in input_lines:#提取input.txt中的数据
        #print "index of input data"
        if j==0:
        	wuliMachine=item.split(" ")
        	cpu_scale=wuliMachine[0]
        	mem_scale=int(wuliMachine[1])*1024
        if j>2 and j<(length-5):
        	flavor_scale.append(item.strip())#flavor名称+规格
        if j==(length-4):
        	kind_yuce=item.strip()#需要计算的是CPU还是Mem
        if j==(length-2):
        	Strart_time=item.strip().split(" ")[0]#需要预测的起始时间
        if j==(length-1):
        	End_time=item.strip().split(" ")[0]#需要预测的截止时间
        j=j+1
    #print type(flavor_kind)
    Strart_time_data=datetime.datetime.strptime(Strart_time, '%Y-%m-%d')
    End_time_data=datetime.datetime.strptime(End_time, '%Y-%m-%d')
    day_span=(End_time_data - Strart_time_data).days#需要预测的时间的跨度
    return cpu_scale,mem_scale,kind_yuce,day_span,flavor_scale

def read_train_data_accordingTo_input_data(ecs_lines,flavor_scale):
    len_flavor_scale=len(flavor_scale)

    input_flavor_scale_dict={}
    flavor_k=[]#提取flavor_scale中的flavor类型名字
    for i in range(len_flavor_scale):
        val=flavor_scale[i].split(' ')
        input_flavor_scale_dict[val[0]]={'CPU':int(val[1]),'MEM':int(val[2])}
    	flavor_k.append(val[0])
    start_time_train_data=ecs_lines[0].split("\t")[2].split(' ')[0]
    End_time_train_data=ecs_lines[-1].split("\t")[2].split(' ')[0]
    train_data_start_time_datetime=datetime.datetime.strptime(start_time_train_data, '%Y-%m-%d')
    train_data_end_time_datatime=datetime.datetime.strptime(End_time_train_data, '%Y-%m-%d')
    whole_days_To_train=(train_data_end_time_datatime - train_data_start_time_datetime).days+1

    flavor_date_span={}
    flavor_date_num={}
    for i in range(len_flavor_scale):
    	flavor_date_span[flavor_k[i]]=[]
    	flavor_date_num[flavor_k[i]]=[]

    for item in ecs_lines:#根据input中出现的flavor类型把Traindata中对应类型出现的日期提取出来
    	values=item.split("\t")
    	if values[1] in flavor_k:
    		date_span=(datetime.datetime.strptime(values[2].split(" ")[0], '%Y-%m-%d') - train_data_start_time_datetime).days#此时的时间为str格式，而非datatime格式
    		flavor_date_span[values[1]].append(date_span)
    #print flavor_date_span['flavor1'].count(0)

    for item in flavor_k:
    	for i in range(whole_days_To_train):
    		flavor_date_num[item].append(flavor_date_span[item].count(i))

    return flavor_date_num,flavor_k

def num_yuce(result,flavor_old_num,day_span,flavor_k):

    #flavor_num_span={}
    flavor_num_yuce={}
    flavor_num_span=count_flavor_num_accordingTo_span(flavor_old_num,day_span,flavor_k)
    #print 'flavor_num_span',flavor_num_span

    for item in flavor_k:
    	len_flavor_num_span=len(flavor_num_span[item])
        old_num=flavor_num_span[item]
        flavor_num_yuce[item]=0
        learning_rate = 0.01
        initial_b = 0 # initial y-intercept guess
        initial_m = 0 # initial slope guess
        num_iterations = 1000
        [b, m] = gradient_descent(len_flavor_num_span,old_num, initial_b, initial_m, learning_rate, num_iterations)
        flavor_num_yuce[item]=(len_flavor_num_span+1)*m+b
    int_flavor_num_predict=int_flavor_num_yuce(flavor_num_yuce,flavor_k)
    result=put_yuce_to_result(int_flavor_num_predict,result,flavor_k)
    #print result
    return int_flavor_num_predict,result

def sort_flavor_k(flavor_k):
    sorted_flavor_k=[]
    temp_dict={}
    for i in range(len(flavor_k)):
        temp_dict[flavor_k[i]]=0
    temp_dict = sorted(temp_dict.items(), key = lambda item:int(item[0][6:]),reverse = True)
    [sorted_flavor_k.append(item[0]) for item in temp_dict]
    return sorted_flavor_k

def put_virtual_machine(result,kind_yuce,cpu_scale,mem_scale,int_flavor_num_predict,flavor_k,flavor_scale):
    input_flavor_dict={}

    for i in range(len(flavor_scale)):#将input数据中的flavor变成一个复合字典:{'flavor1':{'cpu':1,'mem':2},'flavor2':}
        val=flavor_scale[i].split(' ')
        input_flavor_dict[flavor_k[i]]={'CPU':int(val[1]),'MEM':int(val[2])}

    sorted_flavor_k=sort_flavor_k(flavor_k)

    #-------摆放真正开始---------
    k=0
    p=0
    CPU_list=[]
    MEM_list=[]
    CPU_list.append(cpu_scale)
    MEM_list.append(mem_scale)
    where_dict={1:{},}
    for item in sorted_flavor_k:
        #print 'item:',item
        while int_flavor_num_predict[item] > 0:
            for i in range(k+1):
                label_decision = True
                if int(CPU_list[i]) >= input_flavor_dict[item]['CPU'] and int(MEM_list[i]) >= input_flavor_dict[item]['MEM']:
                    CPU_list[i] = int(CPU_list[i]) - input_flavor_dict[item]['CPU']
                    MEM_list[i] = int(MEM_list[i]) - input_flavor_dict[item]['MEM']
                    int_flavor_num_predict[item] = int_flavor_num_predict[item]-1
                    #print 'CPU_list:',CPU_list[i],'MEM_list:',MEM_list[i]

                    label_decision = False
                    if item not in where_dict[i+1]:
                        where_dict[i+1][item] = 1
                    else:
                        where_dict[i+1][item] += 1
                if i < k:
                    continue
                if label_decision and i==k:
                    k=k+1
                    CPU_list.append(cpu_scale)
                    MEM_list.append(mem_scale)
                    CPU_list[k] = int(cpu_scale) - input_flavor_dict[item]['CPU']
                    MEM_list[k] = int(mem_scale) - input_flavor_dict[item]['MEM']
                    int_flavor_num_predict[item] = int(int_flavor_num_predict[item]) - 1
                    where_dict[k+1] = {item:1}
                else:
                    break
    #print 'where_dict:',where_dict
    #return

    #print result
    result.append('\n'+str(len(where_dict)))
    #print result
    for item in where_dict:
        temp = str(item)
        for key in where_dict[item]:
            temp = temp + ' ' + key + ' ' + str(where_dict[item][key])
        result.append(temp)
    return result

def error_calculate(len_old_num, b, m, old_num):
    totalError = 0
    for i in range(len_old_num):
        x = i
        y = old_num[len_old_num-i-1]
        totalError += (y - (m * x + b)) ** 2
    return totalError

def step_gradient(len_old_num, b_current, m_current, old_num, learningRate):
    b_gradient = 0
    m_gradient = 0

    N = float(len_old_num)
    for i in range(len_old_num):
        x = i
        y = old_num[len_old_num-i-1]
        b_gradient += -(2/N) * (y - ((m_current * x) + b_current))
        m_gradient += -(2/N) * x * (y - ((m_current * x) + b_current))
    new_b = b_current - (learningRate * b_gradient)
    new_m = m_current - (learningRate * m_gradient)
    return [new_b, new_m]

def gradient_descent(len_old_num,old_num, starting_b, starting_m, learning_rate, num_iterations):
    b = starting_b
    m = starting_m
    for i in range(num_iterations):
        b, m = step_gradient(len_old_num, b, m, old_num, learning_rate)
    return [b, m]

def count_flavor_num_accordingTo_span(flavor_old_num,day_span,flavor_k):
	flavor_num_span={}
	for item in flavor_k:
		flavor_num_span[item]=[]
		len_temp=len(flavor_old_num[item])
		cir_day=len_temp/day_span
		plus_temp=0
		total_sum=0
		'''
		if len_temp%day_span==0:
			for j in range(cir_day):
				sum_temp=0
				for i in range(len_temp-plus_temp- cir_day,len_temp - plus_temp):
					sum_temp+=flavor_old_num[item][i]
				plus_temp+=cir_day
				flavor_num_span[item].append(sum_temp)
		else:
			for i in range(cir_day):
				sum_temp=0
				for i in range(len_temp-plus_temp- cir_day,len_temp - plus_temp):
					sum_temp+=flavor_old_num[item][i]
				plus_temp+=cir_day
				flavor_num_span[item].append(sum_temp)
				total_sum+=sum_temp
		'''
		for j in range(cir_day):
			sum_temp=0
			for i in range(len_temp-plus_temp- cir_day,len_temp - plus_temp):
				sum_temp+=flavor_old_num[item][i]
			plus_temp+=cir_day
			flavor_num_span[item].append(sum_temp)
	return flavor_num_span

def int_flavor_num_yuce(flavor_num_yuce,flavor_k):
    int_flavor_num_predict={}
    for item in flavor_k:
        if flavor_num_yuce[item]>0:
            int_flavor_num_predict[item]=int(round(flavor_num_yuce[item]))
        else:
            int_flavor_num_predict[item]=0
    return int_flavor_num_predict

def put_yuce_to_result(int_flavor_num_predict,result,flavor_k):
    num=0
    for item in flavor_k:
        num=num+int(int_flavor_num_predict[item])
    result.append(num)
    for item in flavor_k:
        result.append(str(item)+' '+str(int_flavor_num_predict[item]))
    return result
