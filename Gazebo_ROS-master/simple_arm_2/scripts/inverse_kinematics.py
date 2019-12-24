#!/usr/bin/env python
# license removed for brevity

import kdl_parser_py.urdf
import PyKDL as kdl


#setup KDL
filename = "./src/simple_arm_2/urdf/simple_arm.urdf"
(ok, tree) = kdl_parser_py.urdf.treeFromFile(filename)
chain = tree.getChain("world", "link4")
t = kdl.Tree(tree)
fksolverpos = kdl.ChainFkSolverPos_recursive(chain)
iksolvervel = kdl.ChainIkSolverVel_pinv(chain)
iksolverpos = kdl.ChainIkSolverPos_NR(chain,fksolverpos,iksolvervel)
print "\n"


#first test
#set joint angle, then calcu forward cartesian coordinate, and then
#calcu backward joint angle from cartesian coordinate
def first_test():
	#set initila joint argument
	q_init=kdl.JntArray(chain.getNrOfJoints())
	for i in range(q_init.rows()):
		q_init[i]=0.0

	q_solved=kdl.JntArray(chain.getNrOfJoints())
	F1=kdl.Frame.Identity()

	#joint angle to cartesian coordinate
	fksolverpos.JntToCart(q_init,F1)
	print "F1.p",F1.p
	print F1.M.GetQuaternion()

	#cartesian coordinate to joint anlge
	q_zero=kdl.JntArray(chain.getNrOfJoints())
	iksolverpos.CartToJnt(q_zero,F1,q_solved)
	print q_solved

#second test
#set joint angle differentry
def second_test():
	print "\n second testing"
	#set initila joint argument
	q_init=kdl.JntArray(chain.getNrOfJoints())
	q_init[1]=0.2
	q_init[2]=0.2
	q_init[3]=0.2
	q_solved=kdl.JntArray(chain.getNrOfJoints())
	F1=kdl.Frame.Identity()
	fksolverpos.JntToCart(q_init,F1)
	print "F1.p",F1.p
	print F1.M.GetQuaternion()
	q_zero=kdl.JntArray(chain.getNrOfJoints())
	print "q_zero ",q_zero
	iksolverpos.CartToJnt(q_zero,F1,q_solved)
	print q_solved

#third test
#set cartesain coordinate as Vector and Quaternion, and backward calculation it's joint angle.
def third_test():
	print "\n third testing"
	q_zero=kdl.JntArray(chain.getNrOfJoints())
	F2 = kdl.Frame(kdl.Rotation.Quaternion(0,-0.29552,0,0.955337),kdl.Vector(-0.0529279,0,0.201101))
	#print "q_zero ",q_zero
	q_solved=kdl.JntArray(chain.getNrOfJoints())
	iksolverpos.CartToJnt(q_zero,F2,q_solved)
	print "joint angles"
	print q_solved



#first_test()
#second_test()
third_test()

