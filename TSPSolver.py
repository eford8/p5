#!/usr/bin/python3

import copy
import random
from re import S
from this import s
from which_pyqt import PYQT_VER
rand = random.SystemRandom()
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))




import time
import numpy as np
from TSPClasses import *
import heapq
import itertools
import heapq



class TSPSolver:
	def __init__( self, gui_view ):
		self._scenario = None

	def setupWithScenario( self, scenario ):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution,
		time spent to find solution, number of permutations tried during search, the
		solution found, and three null values for fields not used for this
		algorithm</returns>
	'''

	def defaultRandomTour( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation( ncities )
			route = []
			# Now build the route using the random permutation
			for i in range( ncities ):
				route.append( cities[ perm[i] ] )
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this
		algorithm</returns>
	'''

	def greedy( self,time_allowance=60.0 ):
		pass



	''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints:
		max queue size, total number of states created, and number of pruned states.</returns>
	'''

	def branchAndBound( self, time_allowance=60.0 ):
		C = 1000
		inf = 1000000000
		results = {}
		cities = self._scenario.getCities()
		n = len(cities)
		ncities = 0
		foundTour = False
		count = 0
		bssf = self.defaultRandomTour()['soln']
		maxSizeofQueue = 0
		queue = []
		pruned = 0
		numStates = 0
		start_time = time.time()
		stateMatrix = np.empty((n, n))
		for i in range(n):
			for j in range(n):
				#print(str(i) + "," + str(j))
				#print(cities[i].costTo(cities[j]))
				stateMatrix[i,j] = cities[i].costTo(cities[j])
				#if stateMatrix[i,j] == np.inf:
				#	stateMatrix[i,j] = inf
				#	print(i, " " , j, " infinity" )
		state = State(0,[],stateMatrix)
		numStates += 1
		#print(state.stateMatrix)

		#print(bssf.cost)
		state = self.reduce(state)
		#print(state.cost)
		heapq.heappush(queue, (state.cost + ((n - len(state.listCities)) * C), state.cost, rand.randint(1, 10000), state))
		if(len(queue) > maxSizeofQueue):
			maxSizeofQueue = len(queue)

		#print(state.stateMatrix)
		#print(state.cost)
		#print(queue)


		while len(queue) > 0 and time.time()-start_time < time_allowance:
		#while len(queue) > 0 :
			numCitiesLeft, currentCost, random, currentState = heapq.heappop(queue)
			if(currentCost > bssf.cost):
				pruned += 1
			else:
				citiesSoFar = currentState.listCities[:]
				#print("bssf.cost %d", bssf.cost)
				if len(citiesSoFar) == 0:
					citiesSoFar.append(cities[0])
				for city in cities:
					childCities = citiesSoFar[:]
					childCost = currentCost
					childMatrix = copy.deepcopy(currentState.stateMatrix)
					if(not city in citiesSoFar):
						if((len(citiesSoFar) > 0) and childMatrix[citiesSoFar[-1]._index,city._index] == inf):
							pruned += 1
							numStates += 1
							continue
						childCost += childMatrix[citiesSoFar[-1]._index,city._index]
						childMatrix = self.visitCity(childMatrix, city._index, citiesSoFar[-1]._index)
						childCities.append(city)
						childState = State(childCost, childCities, childMatrix)
						numStates += 1
						childState = self.reduce(childState)
						if(len(childCities) == n):
							tempSolution = TSPSolution(childCities)
							if not np.isinf(tempSolution.cost) and tempSolution.cost < bssf.cost:
								bssf = TSPSolution(childCities)
								foundTour = True
							count += 1
							print("len queue ", len(queue), " bssf ", bssf.cost)
						if(childState.cost > bssf.cost):
							pruned += 1
						else :
							heapq.heappush(queue, (childState.cost + ((n - len(childState.listCities)) * C), childState.cost, rand.randint(1,10000), childState))
							if(len(queue) > maxSizeofQueue):
								maxSizeofQueue = len(queue)


		end_time = time.time()
		while len(queue) > 0:
			numCitiesLeft, currentCost, random, currentState = heapq.heappop(queue)
			if(bssf.cost < currentCost):
				pruned += 1
		results['cost'] = bssf.cost 
		results['time'] = end_time - start_time
		results['count'] = count ## number of solutions found
		results['soln'] = bssf
		results['max'] = maxSizeofQueue
		results['total'] = numStates
		results['pruned'] = pruned
		return results
		#pass



	''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number of solutions found during search, the
		best solution found.  You may use the other three field however you like.
		algorithm</returns>
	'''

	def fancy( self,time_allowance=60.0 ):
		pass

	def reduce(self, s):
		length = len(s.stateMatrix[0])
		
		## reduce rows
		rowNum = 0
		#print("COST BEFORE REDUCTION")
		#print(s.cost)
		#print(s.stateMatrix)
		for row in s.stateMatrix:
			#print("ROW")
			#print(row)
			if(0 not in row):
				#print("reduce")
				minimum = min(row)
				if minimum == np.inf:
					rowNum += 1
					continue
				#print("min")
				#print(minimum)
				colNum = 0
				for i in row:
					#print(i)
					if (i == np.inf):
						colNum += 1
						continue
					elif(i - minimum >= 0):
						i = i - minimum
					else:
						i = 0
						print("HERE")
					s.stateMatrix[rowNum, colNum] = i
					colNum += 1
				s.cost = s.cost + minimum
			rowNum += 1
		
		### reduce columns
		for colNum in range(length):
			col = s.stateMatrix[:,colNum]
			if(0 not in col):
				minimum = min(col)
				if minimum == np.inf:
					continue
				rowNum = 0
				for i in col:
					if (i == np.inf):
						rowNum += 1
						continue
					elif(i - minimum >= 0):
						i = i - minimum
					else:
						i = 0
					s.stateMatrix[rowNum, colNum] = i
					rowNum += 1
				s.cost = s.cost + minimum
		return s
	def visitCity(self, matrix, cityLoc, prevLoc):
		for i in range(len(matrix[0])):
			matrix[prevLoc, i] = np.inf
			matrix[i, cityLoc] = np.inf
		return matrix



