import os
from PySide2.QtCore import Signal
from PySide2.QtGui import QIntValidator, QRegExpValidator
import maya.cmds as mc
from  PySide2 .QtWidgets import QCheckBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget, QListWidget, QAbstractItemView

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

    def SetSaveDir(self, newSaveDir):
        self.saveDir = newSaveDir

    def GetSkeletalMeshSavePath(self):
        #Windows: C:dev\myPrj\Name.fbx
        #Linux/MacOS: ~/dev/myPrj/Name.fbx
        #Path can be c:\dev.myPrj\Name.fbx
        path = os.path.join(self.saveDir, self.fileName + ".fbx") # Is raw path
        return os.path.normpath(path) #Normalize the Path
    
    def GetAnimFolder(self):
        path = os.path.join(self.saveDir, "anim")
        return os.path.normpath(path)
    
    def GetAnimClipSavePath(self, clip: AnimClip):
        path = os.path.join(self.GetAnimFolder(), self.fileName + "_" + clip.subFix+".fbx")
        return os.path.normpath(path)

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
    
    def SaveFiles(self):
        childrenJnts = mc.listRelatives(self.rootJnt, c = True, ad=True, type = "joint")
        allJnts = [self.rootJnt] + childrenJnts
        objectsToExport = allJnts + list(self.meshes)

        mc.select(objectsToExport, r = True)
        skeletalMeshSavePath = self.GetSkeletalMeshSavePath()

        mc.FBXResetExport()
        mc.FBXExportSmoothingGroups('-v', True)
        mc.FBXExportInputConnections('-v', False)

        mc.FBXExport('-f', skeletalMeshSavePath, '-s', True, '-ea', False)

        if not self.animations:
            return
        
        os.makedirs(self.GetAnimFolder(), exist_ok= True)
        mc.FBXExportBakeComplexAnimation('-v', True)
        for anim in self.animations:
            
            animsavePath = self.GetAnimClipSavePath(anim)
            startFrame = anim.frameStart
            endFrame = anim.frameEnd

            mc.FBXExportBakeComplexStart('-v', startFrame)
            mc.FBXExportBakeComplexEnd('-v', endFrame)
            mc.FBXExportBakeComplexStep('-v', 1)

            mc.playbackOptions(e = True, min = startFrame, max = endFrame)
            mc.FBXExport('-f', animsavePath, '-s', True, '-ea', True)
            

    

        
class AnimEntry(QWidget):
    entryNamedChanged = Signal(str)
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

        setRanBtn = QPushButton("[ SET ]")
        setRanBtn.clicked.connect(self.SetRangeBtnClicked)
        self.masterLayout.addWidget(setRanBtn)

        removeBtn = QPushButton("[ DEL ]")
        removeBtn.clicked.connect(self.RemoveBtnClicked)
        self.masterLayout.addWidget(removeBtn)

    def StartFrameChanged(self):
        if self.startFrameLineEdit.text():
            self.animClip.frameStart = int(self.startFrameLineEdit.text())

    def SubfixTextChanged(self):
        if self.subfixLineEdit.text():
            self.animClip.subFix = self.subfixLineEdit.text()
            self.entryNamedChanged.emit(self.animClip.subFix)

    def EndFrameChanged(self):
        if self.endFrameLineEdit.text():
            self.animClip.frameEnd = int(self.endFrameLineEdit.text())


    def ToggleBoxToggled(self):
        self.animClip.shouldExport = not self.animClip.shouldExport

    def SetRangeBtnClicked(self):
        mc.playbackOptions(minTime = self.animClip.frameStart, maxTime = self.animClip.frameEnd, e=True)

    def RemoveBtnClicked(self):
        self.entryRemoved.emit(self.animClip) #Calls the function connected to the entryRemoved Signal.
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

        self.saveFileLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.saveFileLayout)
        fileNameLabel = QLabel("Name: ")
        self.saveFileLayout.addWidget(fileNameLabel)
        self.fileNameLineEdit = QLineEdit()
        self.fileNameLineEdit.setFixedWidth(80)
        self.fileNameLineEdit.setValidator(QRegExpValidator("\w+"))
        self.fileNameLineEdit.textChanged.connect(self.FineNameChanged)
        self.saveFileLayout.addWidget(self.fileNameLineEdit)

        fileDirLabel = QLabel("Save Directory: ")
        self.saveFileLayout.addWidget(fileDirLabel)
        self.saveDirLineEdit = QLineEdit()
        self.saveDirLineEdit.setEnabled(False)
        self.saveFileLayout.addWidget(self.saveDirLineEdit)

        setSaveDirBtn = QPushButton("Dir")
        setSaveDirBtn.clicked.connect(self.SetSaveDirBtnClicked)
        self.saveFileLayout.addWidget(setSaveDirBtn)

        self.savePreviewLabel = QLabel()
        self.masterLayout.addWidget(self.savePreviewLabel)

        saveBth = QPushButton("Save Files")
        saveBth.clicked.connect(self.MayaToUE.SaveFiles)
        self.masterLayout.addWidget(saveBth)

    def UpdateSavePreview(self):
        previewText = ""
        skeletalMeshFilePath = self.MayaToUE.GetSkeletalMeshSavePath()
        previewText += skeletalMeshFilePath
        if self.MayaToUE.animations:
            for anim in self.MayaToUE.animations:
                AnimPath = self.MayaToUE.GetAnimClipSavePath(anim)
                previewText += "\n" + AnimPath
        

        self.savePreviewLabel.setText(previewText)
        self.adjustSize()


    def SetSaveDirBtnClicked(self):
        dir = QFileDialog().getExistingDirectory()
        self.MayaToUE.saveDir = dir
        self.saveDirLineEdit.setText(dir)
        self.UpdateSavePreview()

    def FineNameChanged(self, newName):
        self.MayaToUE.fileName = newName
        self.UpdateSavePreview()

    def AddNewAnimEntryBtnClicked(self):
        newClip = self.MayaToUE.AddAnimClip()
        newEntry = AnimEntry(newClip)
        newEntry.entryRemoved.connect(self.RemoveAnimEntry)
        newEntry.entryNamedChanged.connect(self.UpdateSavePreview)
        self.animEntryLayout.addWidget(newEntry)
        self.UpdateSavePreview()

    def MeshListSelectionChaged(self):
        mc.select(cl=True)

    def RemoveAnimEntry(self, clipToRemove):
        print("Remove Animation Signal Emiited, and received here!")
        self.adjustSize()
        self.MayaToUE.animations.remove(clipToRemove)
        self.UpdateSavePreview()

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

