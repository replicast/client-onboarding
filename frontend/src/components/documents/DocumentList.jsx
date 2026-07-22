import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  LinearProgress,
  Alert,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  TextField,
} from '@mui/material';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import documentService from '../../services/documentService';
import PDFViewer from './PDFViewer';

function DocumentList({ clientId }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [deleteDialog, setDeleteDialog] = useState({ open: false, document: null });
  const [viewerDialog, setViewerDialog] = useState({ open: false, document: null, page: 1, search: '', directUrl: null });
  const [startPages, setStartPages] = useState({});
  const [searchTerms, setSearchTerms] = useState({});
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (clientId) {
      loadDocuments();
    }
  }, [clientId]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await documentService.getDocuments(clientId);
      setDocuments(data);
    } catch (err) {
      setError('Failed to load documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (file.type !== 'application/pdf') {
      setError('Only PDF files are allowed');
      return;
    }

    // Validate file size (50MB max)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('File size must be less than 50MB');
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);
      setError(null);

      await documentService.uploadDocument(clientId, file, (progress) => {
        setUploadProgress(progress);
      });

      // Reload documents list
      await loadDocuments();
    } catch (err) {
      setError('Failed to upload document');
      console.error(err);
    } finally {
      setUploading(false);
      setUploadProgress(0);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDownload = (document) => {
    const url = documentService.getDownloadUrl(document.id);
    window.open(url, '_blank');
  };

  const handleView = async (document) => {
    const page = startPages[document.id] || 1;
    const search = searchTerms[document.id] || '';

    try {
      // Fetch the direct SAS URL (avoids redirect which strips fragments)
      const directUrl = await documentService.getDirectUrl(document.id);
      setViewerDialog({ open: true, document, page, search, directUrl });
    } catch (err) {
      setError('Failed to load document URL');
      console.error(err);
    }
  };

  const handleStartPageChange = (docId, value) => {
    const page = parseInt(value, 10) || 1;
    setStartPages((prev) => ({ ...prev, [docId]: Math.max(1, page) }));
  };

  const handleSearchTermChange = (docId, value) => {
    setSearchTerms((prev) => ({ ...prev, [docId]: value }));
  };

  const handleViewerClose = () => {
    setViewerDialog({ open: false, document: null, page: 1, search: '', directUrl: null });
  };

  
  const handleDeleteClick = (document) => {
    setDeleteDialog({ open: true, document });
  };

  const handleDeleteConfirm = async () => {
    const { document } = deleteDialog;
    if (!document) return;

    try {
      setError(null);
      await documentService.deleteDocument(document.id);
      setDocuments(documents.filter((d) => d.id !== document.id));
    } catch (err) {
      setError('Failed to delete document');
      console.error(err);
    } finally {
      setDeleteDialog({ open: false, document: null });
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialog({ open: false, document: null });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Don't render if no clientId (new client form)
  if (!clientId) {
    return (
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Documents
          </Typography>
          <Typography color="text.secondary">
            Save the client first to upload documents.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Documents</Typography>
          <Button
            variant="contained"
            startIcon={<CloudUploadIcon />}
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            Upload PDF
          </Button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            accept="application/pdf"
            style={{ display: 'none' }}
          />
        </Box>

        {uploading && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Uploading... {uploadProgress}%
            </Typography>
            <LinearProgress variant="determinate" value={uploadProgress} />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {loading ? (
          <LinearProgress />
        ) : documents.length === 0 ? (
          <Typography color="text.secondary" sx={{ py: 2 }}>
            No documents uploaded yet.
          </Typography>
        ) : (
          <List>
            {documents.map((doc) => (
              <ListItem key={doc.id} divider>
                <ListItemIcon>
                  <PictureAsPdfIcon color="error" />
                </ListItemIcon>
                <ListItemText
                  primary={doc.original_filename}
                  secondary={`${documentService.formatFileSize(doc.file_size)} - ${formatDate(doc.created_at)}`}
                />
                <ListItemSecondaryAction sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TextField
                    size="small"
                    label="Search"
                    value={searchTerms[doc.id] || ''}
                    onChange={(e) => handleSearchTermChange(doc.id, e.target.value)}
                    inputProps={{ style: { width: '80px' } }}
                  />
                  <TextField
                    type="number"
                    size="small"
                    label="Page"
                    value={startPages[doc.id] || ''}
                    onChange={(e) => handleStartPageChange(doc.id, e.target.value)}
                    inputProps={{ min: 1, style: { width: '50px', textAlign: 'center' } }}
                  />
                  <Tooltip title="View">
                    <IconButton
                      edge="end"
                      onClick={() => handleView(doc)}
                    >
                      <VisibilityIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Download">
                    <IconButton
                      edge="end"
                      onClick={() => handleDownload(doc)}
                    >
                      <DownloadIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton
                      edge="end"
                      onClick={() => handleDeleteClick(doc)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog.open} onClose={handleDeleteCancel}>
        <DialogTitle>Delete Document</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete "{deleteDialog.document?.original_filename}"?
            This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* PDF Viewer Dialog */}
      <Dialog
        open={viewerDialog.open}
        onClose={handleViewerClose}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: { height: '90vh' }
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 1 }} component="div">
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {viewerDialog.document?.original_filename}
          </span>
          <Button onClick={handleViewerClose} variant="outlined" size="small">
            Close
          </Button>
        </DialogTitle>
        <DialogContent sx={{ p: 0, overflow: 'hidden', height: 'calc(100% - 64px)' }}>
          {viewerDialog.document && viewerDialog.directUrl && (
            <PDFViewer
              key={`${viewerDialog.document.id}-${viewerDialog.page}-${viewerDialog.search}`}
              url={viewerDialog.directUrl}
              initialPage={viewerDialog.page}
              initialSearch={viewerDialog.search}
            />
          )}
        </DialogContent>
      </Dialog>
    </Card>
  );
}

export default DocumentList;
