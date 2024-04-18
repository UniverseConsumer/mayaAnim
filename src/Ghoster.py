import maya.cmds as mc
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QAbstractItemView


def GetCurrentFrame():
    return int(mc.currentTime(q=True))

class Ghost:
    def __init__(self):
        self.srcMeshes = set() # a list that has unique elements.
        self.ghostGrp = "ghost_grp"
        self.frameAttr = "frame"
        self.srcAttr = "src"
        self.InitIfGhostGrpNotExist()
        
    def InitIfGhostGrpNotExist(self):
        if mc.objExists(self.ghostGrp):
            storedSrcMeshes = mc.getAttr(self.ghostGrp + "." + self.srcAttr)
            self.srcMeshes = set(storedSrcMeshes.split(","))
            return
        
        mc.createNode("transform", n = self.ghostGrp)
        mc.addAttr(self.ghostGrp, ln = self.srcAttr, dt="string")

 
    def SetSelectedAsSrcMesh(self):
        selection = mc.ls(sl=True)
        self.srcMeshes.clear() #removes all elements in the set
        for selected in selection:
            shapes = mc.listRelatives(selected, s=True) # find all shapes of the selected object
            for s in shapes:
                if mc.objectType(s) == "mesh": # the object is a mesh
                    self.srcMeshes.add(selected) # add the mesh to our set

        mc.setAttr(self.ghostGrp + "." + self.srcAttr, ",".join(self.srcMeshes), type = "string")

    def AddGhost(self):
        for srcMesh in self.srcMeshes:
            currentFrame = GetCurrentFrame()
            ghostName = srcMesh + "_" + str(currentFrame)
            if mc.objExists(ghostName):
                mc.delete(ghostName)


            mc.duplicate(srcMesh, n = ghostName)
            mc.parent(ghostName, self.ghostGrp)
            mc.addAttr(ghostName, ln = self.frameAttr, dv = currentFrame)

    def GoToNextGhost(self):
        frames = self.GetGhostFramesSorted() # find all the frames we have in ascending order
        if not frames: # if there is not frames/Ghost, do nothing
            return
        currentFrame = GetCurrentFrame()
        for frame in frames: #go through each frame
            if frame > currentFrame: # if we find one that is bigger than the current frame, it should be where we can move time slider to
                mc.currentTime(frame, e = True) # e means 'edit', we are editing the time slider to be at frame
                return
            
        mc.currentTime(frames[0], e=True)

    def GoToPrevGhost(self):
        frames = self.GetGhostFramesSorted()
        frames.reverse() #sorts frames list in descending order

        if not frames:
            return
        currentFrame = GetCurrentFrame()
        for frame in frames:
            if frame < currentFrame:
                mc.currentTime(frame, e = True)
                return

            
        mc.currentTime(frames[0], e=True)

    def DeleteGhostOnCurFrame(self):
        currentFrame = GetCurrentFrame()
        ghosts = mc.listRelatives(self.ghostGrp, c=True) #Gets all children of the ghost grp
        for ghost in ghosts:
            ghostFrame = mc.getAttr(ghost + "." + self.frameAttr)
            if ghostFrame == currentFrame:
                self.DeleteGhost(ghost)

    def DeleteGhost(self, ghost):
        mc.delete(ghost)

        
    def GetGhostFramesSorted(self):
        frames = set()
        ghosts = mc.listRelatives(self.ghostGrp, c=True)

        for ghost in ghosts:
            frame = mc.getAttr(ghost + "." + self.frameAttr)
            print(f"Frame is: {frame}")
            frames.add(frame)

        frames = list(frames) # this converts frames to a list
        frames.sort() # sorts frames list to ascending order
        return frames #returns sorted frames


class GhostWidget(QWidget):
    def __init__(self):
        super().__init__() # needed to call if you are inheriting form a parent class
        self.ghost = Ghost() # create a ghost to pass command to
        self.setWindowTitle("Ghoster Poser V1.0") # set the title of the window
        self.masterlayout = QVBoxLayout() # creates a vertial layout
        self.setLayout(self.masterlayout) # tells the window to use the vertical layout created in the previous line

        self.srcMeshList = QListWidget() # create a list to show stuff
        self.srcMeshList.setSelectionMode(QAbstractItemView.ExtendedSelection) # allow multi-selection
        self.srcMeshList.itemSelectionChanged.connect(self.SrcMeshSelectionChanged)
        self.srcMeshList.addItems(self.ghost.srcMeshes)
        self.masterlayout.addWidget(self.srcMeshList) # This adds the lsit created previously to the layout.

        addSrcMeshBtn = QPushButton("Add Source Mesh")
        addSrcMeshBtn.clicked.connect(self.AddSrcMeshBtnClicked)
        self.masterlayout.addWidget(addSrcMeshBtn)

        self.ctrlLayout = QHBoxLayout()
        self.masterlayout.addLayout(self.ctrlLayout)

        addGhostBtn = QPushButton("Add/Update")
        addGhostBtn.clicked.connect(self.ghost.AddGhost)
        self.ctrlLayout.addWidget(addGhostBtn)

        prevGhostBtn = QPushButton("Previous Ghost")
        prevGhostBtn.clicked.connect(self.ghost.GoToPrevGhost)
        self.ctrlLayout.addWidget(prevGhostBtn)

        nextGhostBtn = QPushButton("Next Ghost")
        nextGhostBtn.clicked.connect(self.ghost.GoToNextGhost)
        self.ctrlLayout.addWidget(nextGhostBtn)

        self.ctrlLayout = QHBoxLayout()
        self.masterlayout.addLayout(self.ctrlLayout)
        
        DelGhostBtn = QPushButton("Delete Ghost on Current Frame")
        DelGhostBtn.clicked.connect(self.ghost.DeleteGhostOnCurFrame)
        self.ctrlLayout.addWidget(DelGhostBtn)
        DelGhostAllBtn = QPushButton("Delete Ghost on All Frames")
        DelGhostAllBtn.clicked.connect(self.ghost.DeleteGhost)
        self.ctrlLayout.addWidget(DelGhostAllBtn)

    def SrcMeshSelectionChanged(self):
        mc.select(cl=True) # Deselects Everything
        for item in self.srcMeshList.selectedItems():
            mc.select(item.text(), add = True)

    def AddSrcMeshBtnClicked(self):
        self.ghost.SetSelectedAsSrcMesh() # asks ghost to populate its srcMeshes with the current selection
        self.srcMeshList.clear() # this clears our list widget
        self.srcMeshList.addItems(self.ghost.srcMeshes) # this adds the srcMeshes collected earlier to the list widget


ghostWidget = GhostWidget()
ghostWidget.show()