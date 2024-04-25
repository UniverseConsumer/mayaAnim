from PySide2.QtCore import Signal
from PySide2.QtGui import QIntValidator, QRegExpValidator
import maya.cmds as mc
from  PySide2 .QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget, QListWidget, QAbstractItemView

class AnimClip:
    def __init__(self):
        self.frameStart = int(mc.playbackOptions(q=True, min = True))
        self.frameEnd = int(mc.playbackOptions(q=True, max = True))
        self.subFix = ""
        self.shouldExport = True



class MayaToUE:
    def __init__(self):
        self.rootJnt = ""
        self.meshes = set()
        self.fileName = ""
        self.animations = []
        self.saveDir = ""

    def AddAnimClip(self): 
        self.animations.append(AnimClip())
        return self.animations[-1]

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
    

        
class AnimEntry(QWidget):
    entryRemoved = Signal(AnimClip)
    def __init__(self, animClip: AnimClip):
        super().__init__()
        self.animClip = animClip
        self.masterLayout = QHBoxLayout()
        self.setLayout(self.masterLayout)

        self.toggleBox = QCheckBox()
        self.toggleBox.setChecked(animClip.shouldExport)
        self.toggleBox.toggled.connect(self.ToggleBoxToggled)
        self.masterLayout.addWidget(self.toggleBox)

        subFixLabel = QLabel("Subfix: ")
        self.masterLayout.addWidget(subFixLabel)
        self.subfixLineEdit = QLineEdit()
        self.subfixLineEdit.setValidator(QRegExpValidator('\w+'))
        self.subfixLineEdit.textChanged.connect(self.SubfixTextChanged)
        self.subfixLineEdit.setText(animClip.subFix)
        self.masterLayout.addWidget(self.subfixLineEdit)


        startFrameLabel = QLabel("Start: ")
        self.masterLayout.addWidget(startFrameLabel)
        self.startFrameLineEdit = QLineEdit()
        self.startFrameLineEdit.setValidator(QIntValidator())
        self.startFrameLineEdit.textChanged.connect(self.StartFrameChanged)
        self.startFrameLineEdit.setText(str(animClip.frameStart))
        self.masterLayout.addWidget(self.startFrameLineEdit)

        endFrameLabel = QLabel("End: ")
        self.masterLayout.addWidget(endFrameLabel)
        self.endFrameLineEdit = QLineEdit()
        self.endFrameLineEdit.setValidator(QIntValidator())
        self.endFrameLineEdit.textChanged.connect(self.EndFrameChanged)
        self.endFrameLineEdit.setText(str(animClip.frameEnd))
        self.masterLayout.addWidget(self.endFrameLineEdit)

        setRanBtn = QPushButton("[ - ]")
        setRanBtn.clicked.connect(self.SetRangeBtnClicked)
        self.masterLayout.addWidget(setRanBtn)

        removeBtn = QPushButton("[ X ]")
        removeBtn.clicked.connect(self.RemoveBtnClicked)
        self.masterLayout.addWidget(removeBtn)

    def StartFrameChanged(self):
        if self.startFrameLineEdit.text():
            self.animClip.frameStart = int(self.startFrameLineEdit.text())

    def SubfixTextChanged(self):
        if self.subfixLineEdit.text():
            self.animClip.subFix = self.subfixLineEdit.text()

    def EndFrameChanged(self):
        if self.endFrameLineEdit.text():
            self.animClip.frameEnd = int(self.endFrameLineEdit.text())


    def ToggleBoxToggled(self):
        self.animClip.shouldExport = not self.animClip.shouldExport

    def SetRangeBtnClicked(self):
        mc.playbackOptions(minTime = self.animClip.frameStart, maxTime = self.animClip.frameEnd, e=True)

    def RemoveBtnClicked(self):
        self.deleteLater() #Remove this widget the next time it is proper.


class MayaToUEWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.MayaToUE= MayaToUE()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.setFixedWidth(500)
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
        self.meshList.setFixedHeight(80)
        self.masterLayout.addWidget(self.meshList)
        assignSelectedMeshBtn = QPushButton("Assign Selected Meshes")
        assignSelectedMeshBtn.clicked.connect(self.AssignSelectedMeshBtnClicked)
        self.masterLayout.addWidget(assignSelectedMeshBtn)

        addAnimEntryBtn = QPushButton("Add new Animation Clip")
        addAnimEntryBtn.clicked.connect(self.AddNewAnimEntryBtnClicked)
        self.masterLayout.addWidget(addAnimEntryBtn)

        self.animEntryLayout = QVBoxLayout()
        self.masterLayout.addLayout(self.animEntryLayout)

    def AddNewAnimEntryBtnClicked(self):
        newClip = self.MayaToUE.AddAnimClip()
        newEntry = AnimEntry(newClip)
        self.animEntryLayout.addWidget(newEntry)

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

