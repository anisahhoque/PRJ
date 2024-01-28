

class Node:
    def __init__(self,nodeName,nextNode):
        self.name = nodeName
        self.nextNode = nextNode

    def getNextNode(self):
        return self.nextNode
    

objectOne = Node("a","b")
objectTwo = Node("b","c")

total = 0
my_stack = []
stacklimit = 4

def display(0): 
  for i in range(len(my_stack)-1,-1,-1):
    print(my_stack[i])

while total == 0:
  askstack = input("would you like to push or pop ")
  if askstack == 'push':
    if len(my_stack) < stacklimit:
      item = input("what would you like to push ")
      my_stack.append(item)
      #print(*my_stack[::-1])
      display(my_stack)
    else:
      print("stack is full")
  elif askstack == 'pop':
    if len(my_stack) > 0:
      my_stack.pop()
      display(my_stack)
    else:
            print("stack is empty")
  else:
    print("please enter a valid input")

    total +=1
     

queue = []
counter = 0 
#procedures
def enqueue(queue):
	if counter <5:
		append = input("what would you like to append \n")
		queue.append(append)
		print(queue)
		
	else:
		print("queue full")

def dequeue(queue):
	if len(queue)>0:
		queue.pop(0)
		print(queue)
	else:
		print("empty queue big sad :(")

while True:
	choice = input("Would you like to enqueue or dequeue \n").lower()
	if choice == "enqueue":
		enqueue(queue)
		counter = counter + 1
	elif choice =="dequeue":
		dequeue(queue)
	else:
	 print("?")
      
array = []
array = [None,0,0,0,0] #defining the size of the array