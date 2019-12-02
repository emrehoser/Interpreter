_code=str()								#global variable for the python code to be generated upon compilation
_block=str()								#temporary global variable to store a loop body under processing
_for=bool()								#boolean stating whether a for loop is being processed

#INTERNAL IMPLEMENTATION PART

import math
import sys

def tr(arg):								#transpose
	if(type(arg)==matrix or type(arg)==vector):			#argument type checking
		rows=len(arg.data[0])
		cols=len(arg.data)
		res=matrix(cols,rows)					#create a new matrix that is transposed and return it
		res.data=[[arg.data[col][row] for col in range(cols)] for row in range(rows)]
		return res
	else:								#if it is a scalar, just return itself.
		return arg

def vecdot(x,y,m,n,k):							#helper function for matrix multiplication
	return sum([x[N][m]*y[k][N] for N in range(n)])


def myrange(a,b,c): 							#for translating inclusion convention of matlang language
	return range(a,b+1,c)


def sqrt(n):								#use the embedded sqrt function
	return math.sqrt(n)


def printsep():								#function exactly as specified in matlang 
	print("-"*10)


def countcolon(string):							#counts the colons of the loop header to determine depth of the loop
	_cnt=0
	for _ch in string:
		if(_ch==':'):
			_cnt=_cnt+1
	return _cnt


def myexit(message):							#used for printing error messages throughout the code
	print(message)
	exit()


def checkset(mat,list):							#error check for dimension of the list supplied to set
	if len(list)!=len(mat.data)*len(mat.data[0]):
		myexit("Incorrect initialization length")		#exit in case of error

def checkadd(lhs,rhs):							#check the dimensions of addition operands
	if (len(lhs.data)!=(len(rhs.data)))or((len(lhs.data[0]))!=(len(rhs.data[0]))):
		myexit("Addition incompatibility")			#exit in case of error

def checkmul(lhs,rhs):							#check the dimensions of the multipllication operands
	if len(lhs.data)!=len(rhs.data[0]):				#cols of left ?= rows of right
		myexit("Multiplication incompatibility")

class matrix:								#main class for the matlang
	def __init__(self,argn,argm):					#constructor
		self.data=[[0.0]*argn]*argm #n->nrows, m->ncols
		self.n=argn
		self.m=argm
	def __str__(self):						#default string convertor for matrices(also vectors) for print() method
		result=str()
		for i in range(self.n):
			if(i!=0):
				result+="\n"
			for j in range(self.m):
				result+=('%.7f' % self.data[j][i]).rstrip('0').rstrip('.')#floating point formatting 
		return result	
	def set(self,numbers):						#for value assignment of vectors and scalars
		checkset(self,numbers)					#check dimensions
		ncols=len(self.data)
		nrows=len(self.data[0])
		self.data=[[numbers[row*ncols+col] for row in range(nrows)] for col in range(ncols)]
	def __add__(self, other):					#addition operator overload
		checkadd(self,other)					#check for compatibility
		ncols=len(self.data)
		nrows=len(self.data[0])
		result=matrix(nrows,ncols)				#create a matrix object, set, and return it 
		result.data=[[self.data[col][row]+other.data[col][row] for row in range(nrows)]for col in range(ncols)]		
		return result		
	def __sub__(self,other):					#substraction operator overload
		checkadd(self,other)					#the same compatibility as addition
		ncols=len(self.data)
		nrows=len(self.data[0])
		result=matrix(nrows,ncols)				#create a result object, set its values and return it
		result.data=[[self.data[col][row]-other.data[col][row] for row in range(nrows)]for col in range(ncols)]
		return result
	def __mul__(self,other):					#multiplication overload
		if (type(other)==float or type(other)==int):		#if it is scalar-matrix(vector) product
			res=matrix(len(self.data[0]),len(self.data))		
			for i in range(len(self.data)):
				for j in range(len(self.data[0])):
					res.data[i][j]=self.data[i][j]*other	#simply multiply every element with the scalar
			return res
		else:							#matrix-matrix multiplication
			checkmul(self,other)
			m=len(self.data[0])#rows of left
			n=len(self.data)#cols of left
			n=len(other.data[0])#rows of right
			k=len(other.data)#cols of right
			if (m==1 and k==1):				#inner product of two vectors RETURNS A SCALAR
				return vecdot(self.data,other.data,0,n,0)
			else:						#generic linear-algebraic product (makes use of vecdot() )
				result=matrix(m,k)
				result.data=[[vecdot(self.data,other.data,row,n,col) for row in range(m)]for col in range(k)]
				return result
	def __rmul__(self,other):					#makes scalar-nonscalar product commutative
		if (type(other)==float or type(other)==int):
			return self*other
		else:
			return NotImplemented				#to avoid confusion with non-commutative linear-algebraic product
	def __getitem__(self,indext):					#indexed element access operator overload
		if(type(indext)==type((1,1))):				#if the argument is a tuple (two indices)
			index1,index2=indext				#seperate the indices supplied
			if(index1 > len(self.data[0]) or index1 < 1):	#error checking
				myexit("Index out of range error!")
			if(index2 > len(self.data) or index1 < 1):
				myexit("Index out of range error!")
			return self.data[index2-1][index1-1]		#return the specified element
		else:							#if a single argument is supplied
			if(indext>len(self.data[0]) or indext<1):	#then check if it is just a vector
				myexit("Index out of range error!")
			return self.data[0][indext-1]

class vector(matrix):							#vector child class
	def __init__(self,size):					#1-D constructor
		super().__init__(size,1)
	def __getitem__(self,index):					#vector-specific index access overload
		if(len(self.data[0])<index or index<1):			#bounds-check for the index
			myexit("Index out of range")
		return self.data[0][index-1]				#return the element


def choose(e1,e2,e3,e4):						#conditional block of matlang, exactly as specified
	if e1==0:
		return e2
	if e1>0:
		return e3
	if e1<0:
		return e4


#DETERMINATE INTERPRETATION PART

def assignment(line):							#translate assignment statement
	global _code
	name=line.split('=')[0].split()[0]				#fetch the variable name
	arg=list(map(float,line.split("=")[1].strip(" }{ ").split()))	#fetch the rvalue into a python list
	_code+=name+".set("+str(arg)+")\n"				#program set() to be called


def statement(line):							#any input line is processed here
	global _code							#see the top of the page for globals
	global _for
	global _block
	if(len(line.split())==0):					#do not process whitespace lines
		return
	if(line.split("(")[0].split()[0]=="for"):			#if a loop is beginning
		_for=True						#then switch _for to be true
	if(_for):							#while processing a for block
		_block+=line+"\n"					#accumulate the block
		if(line.find("}")!=-1):					#then when the block ends
			_for=False					#deactivate loop processing and
			loop()						#call the loop processor
	elif matchassignment(line):					#process if the line is an assignment
		assignment(line)
	elif matchdefinition(line):					#process if the line is a definition
		definition(line)
	else:
		_code+=line+"\n"					#if the line is not one of specific cases, then our matrix framework can directly process it


def definition(line):							#processing a definition
	global _code
	if(line.split()[0]=="scalar"):					#if it is a scalar definition
		_code+=line.split()[1]+"=float()\n"			#program a scalar definition in python with the same id
	else:								#for vector and matrix
		type=line.split()[0]					#fetch the type name
		var=line.split("[")[0].split()[1]			#fetch the variable name
		args=line.split("[")[1].split("]")[0]			#fetch the dimensions(either integer or tuple)
		_code+=var+"="+type+"("+args+")\n"			#program the equivalent python declaration with what is fetched above


def loop():	
	global _block
	splitted=_block.split("{")
	executable=splitted[1].split("}")[0]
	header=splitted[0]						#divide the for block into header and executable parts
	if (countcolon(header)==4):					#if it is a nested for
		nestedfor(header,executable)				#call the nester for generator with header and code
	if (countcolon(header)==2):					#and vice versa
		myfor(header,executable)
	_block=""							#flush the stored data in _block

def myfor(header,executable):						#single loop generator
	global _code
	lines=executable.split("\n")					#split every executable line
	ins=header.split(" in ")
	ins[0]=ins[0].lstrip("for")
	ins[0]=ins[0].lstrip(" (")
	ins[1]=ins[1].rstrip(") ")					#fetch loop variable and range from loop header
	_code+=("for "+str(ins[0])+" in myrange("+ins[1].replace(':',',')+"):\n") #generate the corresponding for header in python
	for line in lines :						#then for every executable line
		#_code+="\t"						#(there is indentation in the input anyway)
		statement(line)						#put the statements into the block and execute

def nestedfor(header,executable):					#nested loop processor
	global _code
	lines=executable.split("\n")
	ins=header.split(" in ")
	ins[0]=ins[0].lstrip("for")
	ins[0]=ins[0].lstrip(" (")
	ins[1]=ins[1].rstrip(") ")					#same as myfor but two loop variables and ranges feched together
	indices=ins[0].split(",")					#seperate inner and outer loop variables
	ranges=ins[1].split(",")					
	_code+=("for "+indices[0]+" in myrange("+ranges[0].replace(':',',')+"):\n")#print corresponding python loop headers
	_code+=("	for "+indices[1]+" in myrange("+ranges[1].replace(':',',')+"):\n")
	for line in lines:						#then process the statements inside the block(with extra indentation)
		statement("\t"+line)
	



#MATCHING
def matchassignment(line):						#check if a statement is assignment(helper for statement()) 
	if (line.find("=")!=-1 and line.find("{")!=-1):			#look for tokens specific for this type of statement
		return True
	else:
		return False


def matchdefinition(line):						#check if a statement is definition(helper for statement())
	word=line.split()[0]						#check for definition keywords as the first word
	if (word=="vector" or word=="scalar" or word=="matrix"):	
		return True
	else:
		return False


#DRIVER CODE

fname=str(sys.argv[1])							#open the input file with the name specified as CL argument
with open(fname,'r') as infile:
	strstr=infile.read()						#read the contents of the input program into a string

for stat in strstr.split("\n") :					#the main loop that calls statement for every line
	statc=stat.split("#")[0]
	statr=stat.replace("}"," }")
	statement(statc)

exec(_code)								#execute the python code compiled
