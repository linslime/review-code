import math
import multiprocessing
import random
import numpy as np
import pandas as pd


class Config:
	# 样本数量
	data_size = 10000
	# 每个样本包含正弦函数数量
	trigonometric_functions_number = 3
	# 开始采样的时间
	start_time = 0
	# 结束采样的时间
	end_time = 1000
	# 步长
	step = 0.1
	# 进程数
	processes_count = 12
	# param数据保存路径
	param_path = './params.csv'
	# 信号数据保存路径
	signal_data_path = './signal_data.csv'


def create_wave():
	# 创建任务
	task_list = list()
	for i in range(Config.data_size):
		trigonometric_functions = list()
		for j in range(Config.trigonometric_functions_number):
			A, w, v = random.uniform(1, 10), random.uniform(0, 2 * math.pi), random.uniform(0, 2 * math.pi)
			trigonometric_functions.append([A, w, v])
		task_list.append((i, trigonometric_functions))
	
	# 创建任务队列
	task_queue = multiprocessing.Manager().Queue()
	for i in range(Config.data_size):
		task_queue.put(task_list[i])
	# 创建结果队列
	result_queue = multiprocessing.Manager().Queue()
	# 创建锁
	lock = multiprocessing.Manager().Lock()
	# 创建多进程
	processes = list()
	for i in range(Config.processes_count):
		process = multiprocessing.Process(target=run_create_wave, args=(task_queue, result_queue, lock))
		process.start()
		processes.append(process)
	# 等待多进程完成
	for process in processes:
		process.join()
	# result存放结果
	result = list()
	for i in range(Config.data_size):
		result.append(result_queue.get())
	# 保存参数结果, 改变task_list结构
	params = pd.DataFrame([[task_list[i][0]] + [task_list[i][1][j][k] for j in range(len(task_list[i][1])) for k in range(len(task_list[i][1][j]))] for i in range(len(task_list))])
	# 保存结果，改变result结构
	result = pd.DataFrame([[result[i][0]] + [result[i][1][j] for j in range(len(result[i][1]))]for i in range(len(result))])
	params.to_csv(Config.param_path)
	result.to_csv(Config.signal_data_path)
	
	
def create_one_wave(params):
	data_list = list()
	for j in np.arange(Config.start_time, Config.end_time, Config.step):
		value = 0
		for k in params:
			A, w, v = k
			value += A * math.sin(w * j + v)
		data_list.append(value)
	return data_list


def run_create_wave(task_queue, result_queue, lock):
	while True:
		lock.acquire()
		if not task_queue.empty():
			index, task = task_queue.get()
			lock.release()
			data = create_one_wave(task)
			result_queue.put((index, data))
			
		else :
			lock.release()
			break

	
if __name__ == '__main__':
	create_wave()
	