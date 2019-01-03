
from collections import OrderedDict
from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QItemSelectionModel

from .VFS_Item import VFS_Item

class VFS_Tree_Model(QStandardItemModel):
    '''
    Model to represent a tree layout of the VFS.

    Attributes:
    * path_item_dict
      - Dict, keyed by virtual_path, holding all VFS_Items, including
        directories, with a top node at ''.
    * qt_view
      - Tree view in qt showing this model.

    TODO: remove/update as needed.
    * last_selected_item_label
      - Text name of the last selected item.
      - Unlike the built-in QTreeWidget version, this will only hold
        active items, not table headers.
    * item_dict
      - Dict, keyed by label, of QTreeWidgetItem leaf nodes.
      - Note: this could be unsafe if a label is used more than once.
    * branch_dict
      - Dict, keyed by label, holding QTreeWidgetItem branch nodes.
    '''
    def __init__(self, window, qt_view):
        super().__init__(window)
        self.path_item_dict = None
        self.last_selected_item_label = None
        self.qt_view = qt_view
        self.window = window
        self.item_dict   = {}
        self.branch_dict = {}        
        return
        

    def Set_File_Listing(self, virtual_paths):
        '''
        Fill in the tree with the given file system contents.

        * virtual_paths
          - List of strings, virtual paths to be included.
        '''        
        ## Record the expansion state of items.
        ## The goal is that all labels currently expanded will get
        ## automatically reexpanded after a refresh.
        ## This is somewhat annoying since it has to go through the
        ##  qt_view with index translation.
        #expanded_labels = [label for label, item in self.branch_dict.items() 
        #                   if self.qt_view.isExpanded(self.indexFromItem(item))]


        # Clear out old table items.
        self.clear()
        #self.item_dict  .clear()
        #self.branch_dict.clear()        

        # Convert to vfs items.
        self.Convert_Paths_To_VFS_Items(virtual_paths)

        # Grab the top node.
        top_item = self.path_item_dict['']

        # Convert its children to Q items and add them.
        for q_item in top_item.Get_Child_Q_Items(
                include_folders = True, 
                recursive = True
            ):
            self.appendRow(q_item)
            

        ## Try to find the item matching the last selected non-branch item's
        ##  text, and restore its selection.
        #if self.last_selected_item_label in self.item_dict:
        #    # Look up the item.
        #    item = self.item_dict[self.last_selected_item_label]
        #    # Select it (highlights the line).
        #    self.qt_view.selectionModel().setCurrentIndex(
        #        self.indexFromItem(item), QItemSelectionModel.SelectCurrent)
        #    #self.setCurrentItem(item, True)
        #    # Set it for display.
        #    self.Change_Item(item)
        #
        #else:
        #    # TODO: clear the display.
        #    pass
        #
        ## Reexpand nodes based on label matching.
        #for label, item in self.branch_dict.items():
        #    if label in expanded_labels:
        #        self.qt_view.setExpanded(self.indexFromItem(item), True)
        #        
        ## TODO: save expansion state across sessions.
        return


    def Convert_Paths_To_VFS_Items(self, virtual_paths):
        '''
        Generate VFS_Items for the given virtual_paths.
        Returns a dict, keyed by virtual_path (partials for folders),
        holding the items. There will be more entries in this dict
        than there are original file virtual_paths due to the extra
        for directories.
        The top level node will have an empty path string.
        '''
        path_item_dict = {}
        def Record_Parents(vfs_item):
            '''
            Recursive function to record parent folders for a given
            item, adding this item to its parent.
            '''
            # If this vfs_item is root, return early.
            if vfs_item.virtual_path == '':
                return
            # Look up the parent folders to reach this file.
            parent_path = vfs_item.parent_path

            # If it is not yet seen, record it as a folder.
            if parent_path not in path_item_dict:
                parent = VFS_Item(
                    virtual_path = parent_path,
                    is_folder = True )
                path_item_dict[parent_path] = parent
                # Record its parents recursively.
                Record_Parents(parent)

            # Add this item to its parent.
            path_item_dict[parent_path].Add_Item(vfs_item)
            return


        # Note: this can take excessive time if the full file
        #  system contents are given; maybe look into it again
        #  if that is ever wanted, but for now rely on the input
        #  paths having been filtered down to text items or maybe some
        #  select binary.
        # Update: removing the VFS_Item creation for files sped this
        #  up a lot, and the file type filter even more so.

        for virtual_path in virtual_paths:

            *parent, name = virtual_path.rsplit('/',1)
            if parent:
                parent_path = parent[0]
            else:
                parent_path = ''

            # Set up the first parent.
            if parent_path not in path_item_dict:
                parent = VFS_Item(
                    virtual_path = parent_path,
                    is_folder = True )
                path_item_dict[parent_path] = parent
                # Record its parents recursively.
                Record_Parents(parent)
                
            # Add this virtual_path to its parent.
            path_item_dict[parent_path].file_paths.append(virtual_path)

            ## Create its item.
            ## TODO: skip file item creation, and just record them
            ## as lists of names, to save tree building time (these
            ## won't display anyway, if placed in the list view instead).
            #vfs_item = VFS_Item(
            #    virtual_path = virtual_path,
            #    is_folder = False )
            #path_item_dict[virtual_path] = vfs_item

            # Fill in its parents.
            #Record_Parents(vfs_item)

        self.path_item_dict = path_item_dict
        return


    #def _Categorize_Virtual_Paths(self, virtual_paths):
    #    '''
    #    Transform a list of virtual paths into a dict of dicts of ...
    #    of dicts or virtual_paths. Each key is a folder name. Files at
    #    a level are collected into the '@files' key, using their
    #    full virtual_path.
    #    '''
    #    top_dict = OrderedDict()
    #    top_dict['@files'] = []
    #
    #    for path in sorted(virtual_paths):
    #
    #        # Break up the pieces; this is safe even if there is
    #        # no '/' present.
    #        *folders, file_name = path.split('/')
    #
    #        # Step through the folders, filling out the dict structure
    #        # and getting the final dict.
    #        this_dict = top_dict
    #        for folder in sorted(folders):
    #
    #            # Build another level if needed.
    #            if folder not in this_dict:
    #                # Give all levels an empty list of files initially.
    #                this_dict[folder] = OrderedDict()
    #                this_dict[folder]['@files'] = []
    #
    #            # Move one level deeper for the next loop iteration.
    #            this_dict = this_dict[folder]
    #
    #        # With no folders present, put the file here.
    #        if not folders:
    #            # Add the file.
    #            this_dict['@files'].append(path)
    #
    #    # Everything should be organized now.
    #    return top_dict
    #


    def Handle_selectionChanged(self, qitemselection = None):
        '''
        A different item was clicked on.
        '''
        # This takes a bothersome object that needs indexes
        # extracted, that then need to be converted to items,
        # instead of just giving the item like qtreewidget.
        new_item = self.itemFromIndex(qitemselection.indexes()[0])
        self.Change_Item(new_item)


    def Change_Item(self, new_item):
        '''
        Change the selected item.
        '''
        # Note: it appears when the tree refreshes this event
        # triggers with None as the selection, so catch that case.
        if new_item == None:
            return

        # Record it for refresh restoration.
        self.last_selected_item_label = new_item.text()
        # Pass the object_view to the display widget.
        self.window.list_model.Update(new_item.vfs_item)
        return


    def Soft_Refresh(self):
        '''
        Does a partial refresh of the table, resetting the 'current'
        values of items and redrawing the table.
        '''
        # Send the selected item off for re-display, if there is
        # a selection.
        if self.last_selected_item != None:
            self.Handle_itemChanged(self.last_selected_item)
        return

