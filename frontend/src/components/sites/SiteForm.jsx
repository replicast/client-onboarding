import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  Grid,
  Snackbar,
  Alert,
  CircularProgress,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import * as atlas from 'azure-maps-control';
import * as atlasDrawing from 'azure-maps-drawing-tools';
import siteService from '../../services/siteService';
import clientService from '../../services/clientService';

function SiteForm() {
  const navigate = useNavigate();
  const { id, clientId } = useParams();
  const isEdit = Boolean(id);
  const mapRef = useRef(null);
  const drawingManagerRef = useRef(null);

  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [client, setClient] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    site_type: '',
    geolocation_polygon: null,
  });
  const [errors, setErrors] = useState({});
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    loadClient();
    if (isEdit) {
      loadSite();
    }
  }, [id, clientId]);

  useEffect(() => {
    // Initialize Azure Maps after component mounts
    const timer = setTimeout(() => {
      initializeMap();
    }, 500);
    return () => clearTimeout(timer);
  }, [formData.geolocation_polygon]);

  const loadClient = async () => {
    try {
      const data = await clientService.getClient(clientId || formData.client_id);
      setClient(data);
    } catch (error) {
      console.error('Failed to load client');
    }
  };

  const loadSite = async () => {
    try {
      setLoading(true);
      const data = await siteService.getSite(id);
      setFormData({
        name: data.name,
        site_type: data.site_type,
        geolocation_polygon: data.geolocation_polygon,
      });
    } catch (error) {
      setSnackbar({ open: true, message: 'Failed to load site', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const initializeMap = () => {
    if (!mapRef.current) return;

    const mapKey = process.env.REACT_APP_AZURE_MAPS_KEY || 'your-azure-maps-key';

    // Initialize map
    const map = new atlas.Map('azureMap', {
      center: [-98, 39],
      zoom: 4,
      language: 'en-US',
      authOptions: {
        authType: 'subscriptionKey',
        subscriptionKey: mapKey,
      },
    });

    map.events.add('ready', () => {
      // Create drawing manager
      const drawingManager = new atlasDrawing.drawing.DrawingManager(map, {
        toolbar: new atlasDrawing.control.DrawingToolbar({
          buttons: ['draw-polygon', 'edit-geometry'],
        }),
      });

      drawingManagerRef.current = drawingManager;

      // If editing and has existing polygon, display it
      if (formData.geolocation_polygon) {
        const dataSource = new atlas.source.DataSource();
        map.sources.add(dataSource);

        const polygon = new atlas.data.Feature(
          new atlas.data.Polygon(formData.geolocation_polygon.coordinates)
        );
        dataSource.add(polygon);

        const polygonLayer = new atlas.layer.PolygonLayer(dataSource, null, {
          fillColor: 'rgba(0, 200, 200, 0.5)',
        });
        map.layers.add(polygonLayer);
      }

      // Listen for shape creation
      map.events.add('drawingcomplete', drawingManager, (shape) => {
        const geoJson = shape.toJson();
        setFormData({ ...formData, geolocation_polygon: geoJson.geometry });
      });
    });

    mapRef.current = map;
  };

  const handleChange = (field) => (event) => {
    setFormData({ ...formData, [field]: event.target.value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: null });
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = 'Site name is required';
    if (!formData.site_type.trim()) newErrors.site_type = 'Site type is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      setSaving(true);
      if (isEdit) {
        await siteService.updateSite(id, formData);
        setSnackbar({ open: true, message: 'Site updated successfully', severity: 'success' });
      } else {
        await siteService.createSite(clientId, formData);
        setSnackbar({ open: true, message: 'Site created successfully', severity: 'success' });
      }
      setTimeout(() => navigate(`/clients/${clientId}/sites`), 1500);
    } catch (error) {
      setSnackbar({
        open: true,
        message: `Failed to ${isEdit ? 'update' : 'create'} site`,
        severity: 'error',
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" mb={3}>
        {isEdit ? 'Edit Site' : 'Add New Site'} - {client?.name}
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Site Name"
                  value={formData.name}
                  onChange={handleChange('name')}
                  error={Boolean(errors.name)}
                  helperText={errors.name}
                  required
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Site Type"
                  value={formData.site_type}
                  onChange={handleChange('site_type')}
                  error={Boolean(errors.site_type)}
                  helperText={errors.site_type}
                  required
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Geolocation Polygon
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Use the drawing tools to draw a polygon on the map
                </Typography>
                <Box
                  id="azureMap"
                  sx={{
                    width: '100%',
                    height: 500,
                    border: '1px solid #ccc',
                    borderRadius: 1,
                  }}
                />
              </Grid>

              <Grid item xs={12}>
                <Box display="flex" gap={2} justifyContent="flex-end">
                  <Button
                    variant="outlined"
                    startIcon={<CancelIcon />}
                    onClick={() => navigate(`/clients/${clientId}/sites`)}
                    disabled={saving}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<SaveIcon />}
                    disabled={saving}
                  >
                    {saving ? 'Saving...' : 'Save'}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
}

export default SiteForm;
