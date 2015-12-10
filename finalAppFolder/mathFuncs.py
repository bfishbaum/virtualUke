
def herosFormula(p1,p2,p3):
	a = distance(p1,p2)
	b = distance(p1,p3)
	c = distance(p2,p3)
	s = (a+b+c)/2

	value1 = (s-a)*(s-b)*(s-c)*(s)
	return value1 ** 0.5

def distance(p1,p2):
	dx = (p2[0]-p1[0])**2
	dy = (p2[1]-p1[1])**2

	return (dx+dy)**0.5
	
def sumListTuple(a):
	result = [0 for i in range(len(a[0]))]
	for tuple in a:
		for i in range(len(tuple)):
			result[i] += tuple[i]
	return result
