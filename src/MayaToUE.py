import maya.cmds as mc
from  PySide2 .QtWidgets import QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget, QListWidget, QAbstractItemView

class MayaToUE:
    def __init__(self):
        self.rootJnt = ""
        self.meshes = set()
        self.fileName = ""
        self.animations = []
        self.saveDir = ""

    def SetSelectedAsRootJnt(self):
        selection = mc.ls(sl=True, type = "joint")
        if not selection:
            return False, "No Joint Selected"
        
        self.rootJnt = selection[0]
        return True, ""


    def TryAddUnrealRootJnt(self):
        if (not self.rootJnt) or (not mc.objExists(self.rootJnt)):
            return False, "ERROR: You Need to Assign a Root Joint First!"        

        #Q = Query, t means Translate, ws means World Space
        currentRootPos = mc.xform(self.rootJnt, q=True, t=True, ws=True)
        if currentRootPos[0] == 0 and currentRootPos[1] == 0 and currentRootPos [2] == 0:
            return False, "ERROR: Root Joint already Exists!"

        rootJntName = self.rootJnt + "_root"
        mc.select(cl=True) #cl = Cancel
        mc.joint(name = rootJntName)
        mc.parent(self.rootJnt, rootJntName)
        self.rootJnt = rootJntName
        return True, ""

    def SetSelectedAsMeshes(self):
        selection = mc.ls(sl=True)
        if not selection:
            return False, "No Mesh Selected"
        
        meshes = set() 
        for sel in selection: # Loop though everything we select
            shapes = mc.listRelatives(sel, s=True) # Find their shape nodes
            if not shapes:
                continue
            for s in shapes: # For each shape node we find
                if mc.objectType(s) == "mesh": #Check if there are mesh shapes
                    meshes.add(sel) # If they are mesh shapes, we will collect tem

        if len(meshes) == 0:
            return False, "No Mesh Selected"
    
        self.meshes = meshes 
        return True, ""
        

class MayaToUEWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.MayaToUE= MayaToUE()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.jntLineEdit = QLineEdit()
        self.jntLineEdit.setEnabled(False) #Make it grayed out
        self.masterLayout.addWidget(self.jntLineEdit)

        setselectedAsRootJntBtn = QPushButton("Set Selected As Root Joint")
        setselectedAsRootJntBtn.clicked.connect(self.SetSelectedAsRootBtnClicked)
        self.masterLayout.addWidget(setselectedAsRootJntBtn)

        addUnrealRootBtn = QPushButton("Add Unreal Root Joint")
        addUnrealRootBtn.clicked.connect(self.AddUnrealRootBtnClicked)
        self.masterLayout.addWidget(addUnrealRootBtn)

        self.meshList = QListWidget()
        self.meshList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.meshList.itemSelectionChanged.connect(self.MeshListSelectionChaged)
        self.masterLayout.addWidget(self.meshList)
        assignSelectedMeshBtn = QPushButton("Assign Selected Meshes")
        assignSelectedMeshBtn.clicked.connect(self.AssignSelectedMeshBtnClicked)
        self.masterLayout.addWidget(assignSelectedMeshBtn)

    def MeshListSelectionChaged(self):
        mc.select(cl=True)

    def AssignSelectedMeshBtnClicked(self):
        success, msg = self.MayaToUE.SetSelectedAsMeshes()
        if success:
            self.meshList.clear()
            self.meshList.addItems(self.MayaToUE.meshes)

        else:
            QMessageBox().warning(self, "Warning", msg)

    def AddUnrealRootBtnClicked(self):
        success, msg = self.MayaToUE.TryAddUnrealRootJnt()
        if success:
            self.jntLineEdit.setText(self.MayaToUE.rootJnt)
        else:
            QMessageBox().warning(self, "Warning", msg)

    def SetSelectedAsRootBtnClicked(self):
        success, msg = self.MayaToUE.SetSelectedAsRootJnt()
        if success:
            self.jntLineEdit.setText(self.MayaToUE.rootJnt)
        else:
            QMessageBox().warning(self, "Warning", msg)
        


mayaToUEWidget = MayaToUEWidget()
mayaToUEWidget.show()

