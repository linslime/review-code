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
	# 进行计算的进程数
	processes_count = 11
	# 保存数据的进程数
	save_result_process_count = 50
	# 数据保存路径
	path = '../data/'


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
	# 创建结果处理锁
	result_lock = multiprocessing.Manager().Lock()
	# 创建多进程保存结果
	for i in range(Config.save_result_process_count):
		process = multiprocessing.Process(target=save_wave, args=(result_queue, result_lock))
		process.start()
		processes.append(process)
	# 等待多进程完成
	for process in processes:
		process.join()
	
	# 保存参数结果, 改变task_list结构
	params = pd.DataFrame([[task_list[i][0]] + [task_list[i][1][j][k] for j in range(len(task_list[i][1])) for k in range(len(task_list[i][1][j]))] for i in range(len(task_list))])
	params.to_csv(Config.path + 'params.csv')
	
	
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
		else:
			lock.release()
			break

	
def save_wave(queue, lock):
	while True:
		lock.acquire()
		if not queue.empty():
			index, data = queue.get()
			lock.release()
			df = pd.DataFrame(data)
			df.to_csv(Config.path + 'wave/' + str(index) + '.csv')
		else:
			lock.release()
			break

	
if __name__ == '__main__':
	create_wave()
	