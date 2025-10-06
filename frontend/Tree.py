from typing import Any, Dict, Optional

from PySide6.QtCore import Signal, Qt, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView


class Tree(QWidget):
    """
    Skeleton Tree view widget.

    Responsibilities:
    - Draw or map a directory structure into a visual tree.
    - Emit treeItemClicked with an identifier/path when a node is clicked.
    """

    treeItemClicked = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Initialize the tree view and model
        self.tree_view = QTreeView(self)
        self.tree_model = QStandardItemModel(self)
        self.tree_model.setHorizontalHeaderLabels(['Directory'])
        self.tree_view.setModel(self.tree_model)
        
        # Connect the clicked signal
        self.tree_view.clicked.connect(self._on_item_clicked)
        
        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree_view)
        self.setLayout(layout)

    def draw_tree(self, directory_structure: Dict[str, Any]) -> str:
        """
        Build and display the tree structure from the nested dictionary.
        Returns a textual representation of the tree (for debugging/logging).
        """
        # Clear existing tree
        self.tree_model.clear()
        self.tree_model.setHorizontalHeaderLabels(['Directory'])
        
        root_node = self.tree_model.invisibleRootItem()
        
        # Build the tree recursively
        self._build_tree_recursive(directory_structure, root_node, "")
        
        # Expand the first level by default
        self.tree_view.expandToDepth(0)
        
        return self._tree_to_string(directory_structure)

    def _build_tree_recursive(
        self, 
        node_dict: Dict[str, Any], 
        parent_item: QStandardItem, 
        current_path: str
    ) -> None:
        """
        Recursively build the QStandardItemModel tree from the nested dictionary.
        
        Args:
            node_dict: The current level of the directory structure dictionary
            parent_item: The parent QStandardItem to attach children to
            current_path: The accumulated path string to this node
        """
        if not isinstance(node_dict, dict):
            return
        
        # Sort keys for consistent display, but handle '__assets__' specially
        sorted_keys = sorted(
            key for key in node_dict.keys() if key != '__assets__'
        )
        
        for key in sorted_keys:
            value = node_dict[key]
            
            # Build the path for this node
            new_path = f"{current_path}/{key}" if current_path else key
            
            # Create a tree item for this directory/node
            item = QStandardItem(key)
            
            # Store the full path in UserRole for retrieval on click
            item.setData(new_path, Qt.ItemDataRole.UserRole)
            
            # Check if this node has assets
            has_assets = isinstance(value, dict) and '__assets__' in value
            if has_assets:
                assets = value.get('__assets__', [])
                # Optionally store assets data on the item
                item.setData(assets, Qt.ItemDataRole.UserRole + 1)
            
            # Add the item to the parent
            parent_item.appendRow(item)
            
            # Recursively process children if this is a dict (directory)
            if isinstance(value, dict):
                self._build_tree_recursive(value, item, new_path)

    def _on_item_clicked(self, index: QModelIndex) -> None:
        """
        Handle tree item clicks and emit the treeItemClicked signal.
        
        Args:
            index: The QModelIndex of the clicked item
        """
        if not index.isValid():
            return
        
        # Retrieve the path stored in UserRole
        path = index.data(Qt.ItemDataRole.UserRole)
        
        if path:
            self.treeItemClicked.emit(path)

    def _tree_to_string(
        self, 
        node_dict: Dict[str, Any], 
        indent: int = 0
    ) -> str:
        """
        Convert the tree structure to a textual representation for debugging.
        
        Args:
            node_dict: The directory structure dictionary
            indent: Current indentation level
            
        Returns:
            String representation of the tree
        """
        if not isinstance(node_dict, dict):
            return ""
        
        result = []
        prefix = "  " * indent
        
        # Sort keys for consistent output
        sorted_keys = sorted(
            key for key in node_dict.keys() if key != '__assets__'
        )
        
        for key in sorted_keys:
            value = node_dict[key]
            
            # Check if this node has assets
            asset_marker = ""
            if isinstance(value, dict) and '__assets__' in value:
                asset_count = len(value.get('__assets__', []))
                asset_marker = f" [{asset_count} asset(s)]"
            
            result.append(f"{prefix}{key}{asset_marker}")
            
            # Recursively process children
            if isinstance(value, dict):
                child_str = self._tree_to_string(value, indent + 1)
                if child_str:
                    result.append(child_str)
        
        return "\n".join(result)
    
    def expand_to_depth(self, depth: int) -> None:
        """
        Expand the tree to a specific depth level.
        
        Args:
            depth: The depth level to expand to (0 = first level only)
        """
        self.tree_view.expandToDepth(depth)
    
    def collapse_all(self) -> None:
        """Collapse all tree items."""
        self.tree_view.collapseAll()
    
    def expand_all(self) -> None:
        """Expand all tree items."""
        self.tree_view.expandAll()
