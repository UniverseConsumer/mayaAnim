import maya.cmds as mc
from  PySide2 .QtWidgets import QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget

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

    def SetSelectedAsMeshes(self):
        selection = mc.ls(sl=True)
        if not selection:
            return False, "No Mesh Selected"
        
        meshes = set() 
        for sel in selection: # Loop though everything we select
            shapes = mc.listRelatives(sel, s=True) # Find their shape nodes
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

    def SetSelectedAsRootBtnClicked(self):
        success, msg = self.MayaToUE.SetSelectedAsRootJnt()
        if success:
            self.jntLineEdit.setText(self.MayaToUE.rootJnt)
        else:
            QMessageBox().warning(self, "Warning", msg)
        


mayaToUEWidget = MayaToUEWidget()
mayaToUEWidget.show()

