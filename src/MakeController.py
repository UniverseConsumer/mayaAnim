#Press Alt+Shift+M
import maya.cmds as mc

from PySide2.QtWidgets import QWidget,QLabel, QVBoxLayout, QPushButton

def CreateBox(name, size):
    pntPositions = ((-0.5,0.5,0.5), (0.5,0.5,0.5), (0.5,0.5,-0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5))
    mc.curve(n = name, d=1, p = pntPositions)
    mc.setAttr(name + ".scale", size, size, size, type = "float3")
    mc.makeIdentity(name, a = True) #Freeze Transformation

def CreateCircleController(jnt, size):
    name = "ac_" + jnt
    mc.circle(n = name, nr=(1,0,0), r = size/2)
    ctrlGrpName = name +"_GRP"
    mc.group(name, n=ctrlGrpName)
    mc.matchTransform(ctrlGrpName, jnt)
    mc.orientConstraint(name, jnt)

    return name, ctrlGrpName

def GetObjPos(obj):
    pos = mc.xform(obj, q= True, t = True, ws = True)
    return Vector(pos[0], pos[1], pos[2])

def SetObjPos(obj, pos):
    mc.setAttr(obj + ".translate", pos.x, pos.y, pos.z, type = "float3")

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector (self.x * scalar.x, self.y * scalar.y, self.z * scalar.z)

    def __truediv__(self, scalar):
        return Vector (self.x / scalar.x, self.y / scalar.y, self.z / scalar.z)
    
    def GetLength(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    
    def GetNormalized(self):
        return self/self.GetLength()
    
    def __str__(self):
        return f"<{self.x} {self.y} {self.z}>"
    



class CreateLimbControl:
    def __init__(self):
        self.root = ""
        self.mid = ""
        self.end = ""

    def FindJntBasedOnRootSel(self):
        self.root = mc.ls(sl=True, type = "joint") [0]
        self.mid = mc.listRelatives(self.root, c=True, type="joint") [0]
        self.end = mc.listRelatives(self.mid, c=True, type="joint")[0]

    def RigLimb(self):
        rootCtrl, rootCtrlGrp = CreateCircleController(self.root, 20)
        midCtrl, midCtrlGrp = CreateCircleController(self.mid, 20)
        endCtrl, endCtrlGrp = CreateCircleController(self.end, 20)

        mc.parent(midCtrlGrp, rootCtrl)
        mc.parent(endCtrlGrp, midCtrl)

        ikEndCtrl = "ac_ik_" + self.end
        CreateBox(ikEndCtrl, 10)
        ikEndCtrlGrp = ikEndCtrl + "_GRP"
        mc.group(ikEndCtrl, n = ikEndCtrlGrp)
        mc.matchTransform(ikEndCtrlGrp, self.end)
        mc.orientConstraint(ikEndCtrl, self.end)

        ikHandleName = "ikHandle_" + self.end
        mc.ikHandle(n=ikHandleName, sj = self.root, ee = self.end, sol="ikRPSolver")

        poleVector = mc.getAttr(ikHandleName +" .poleVector")[0]
        poleVector = Vector(poleVector[0], poleVector[1], poleVector[2])
        poleVector = poleVector.GetNormalized()

        rootPos = GetObjPos(self.root)
        endPos = GetObjPos(self.end)

        rootToEndVec = endPos - rootPos

        armHalfLength = rootToEndVec.GetLength()/2
        
        poleVecPos = rootPos + rootToEndVec/2 + poleVector * armHalfLength
        ikMidCtrl = "ac_ik_" + self.mid
        mc.spaceLocator(n = ikMidCtrl)
        ikMidCtrlGrp = ikMidCtrl + "_grp"
        mc.group(ikMidCtrl, n=ikMidCtrlGrp)
        SetObjPos(ikMidCtrlGrp, poleVecPos)
        mc.poleVectorContstriant(ikMidCtrl, ikHandleName)

class CreateLimbControllerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create IkFk Limnb")
        self.setGeometry(100,100,300,300)
        self.masterlayout = QVBoxLayout()
        self.setLayout(self.masterlayout)
        
        hintLabel = QLabel("Please Select the root of the Limb: ")
        self.masterlayout.addWidget(hintLabel)

        findJntsButton = QPushButton("Find Jnts")
        findJntsButton.clicked.connect(self.FindJntBtnClicked)

        self.masterlayout.addWidget(findJntsButton)
        
        self.autoFindJntDisplay = QLabel("")
        self.masterlayout.addWidget(self.autoFindJntDisplay)
        self.adjustSize()

        rigLimbBtn = QPushButton("Rig Limb")
        rigLimbBtn.clicked.connect(self.RigLimbBtnClicked)
        self.masterlayout.addWidget(rigLimbBtn)

        self.createLimbCtrl = CreateLimbControl()

    def FindJntBtnClicked(self):
        self.createLimbCtrl.FindJntBasedOnRootSel()
        self.autoFindJntDisplay.setText(f"{self.createLimbCtrl.root},{self.createLimbCtrl.mid},{self.createLimbCtrl.end}")

    def RigLimbBtnClicked(self):
        self.createLimbCtrl.RigLimb()




ControllerWidget = CreateLimbControllerWidget()
ControllerWidget.show()