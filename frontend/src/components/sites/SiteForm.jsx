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
import siteService from '../../services/siteService';
import clientService from '../../services/clientService';
import COUNTRY_COORDINATES, { DEFAULT_COORDINATES } from '../../data/countryCoordinates';

// Use Azure Maps from CDN (loaded in index.html)
const atlas = window.atlas;

function SiteForm() {
  const navigate = useNavigate();
  const { id, clientId } = useParams();
  const isEdit = Boolean(id);
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const drawingManagerRef = useRef(null);
  const initialPolygonRef = useRef(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [client, setClient] = useState(null);
  const [mapReady, setMapReady] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    site_type: '',
    geolocation_polygon: null,
  });
  const [errors, setErrors] = useState({});
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Load client and site data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const clientData = await clientService.getClient(clientId);
        setClient(clientData);

        if (isEdit) {
          const siteData = await siteService.getSite(id);
          // Store polygon in ref for map initialization
          initialPolygonRef.current = siteData.geolocation_polygon;
          setFormData({
            name: siteData.name,
            site_type: siteData.site_type,
            geolocation_polygon: siteData.geolocation_polygon,
          });
        }
      } catch (error) {
        setSnackbar({ open: true, message: 'Failed to load data', severity: 'error' });
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [id, clientId, isEdit]);

  // Reset map when route changes (different site or client)
  useEffect(() => {
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.dispose();
        mapInstanceRef.current = null;
      }
    };
  }, [id, clientId]);

  // Initialize map once client is loaded and component is ready
  useEffect(() => {
    if (loading || !client) return;

    // If map already exists, dispose it first
    if (mapInstanceRef.current) {
      mapInstanceRef.current.dispose();
      mapInstanceRef.current = null;
    }

    const timer = setTimeout(() => {
      initializeMap();
    }, 100);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading, client]);

  const initializeMap = () => {
    const mapContainer = document.getElementById('azureMap');
    if (!mapContainer || !client) return;

    const mapKey = process.env.REACT_APP_AZURE_MAPS_KEY;
    if (!mapKey) {
      console.error('Azure Maps key not configured');
      return;
    }

    // Get country coordinates for the client's country
    const countryCoords = COUNTRY_COORDINATES[client.country] || DEFAULT_COORDINATES;

    // Initialize map centered on client's country
    const map = new atlas.Map('azureMap', {
      center: countryCoords.center,
      zoom: countryCoords.zoom,
      language: 'en-US',
      authOptions: {
        authType: 'subscriptionKey',
        subscriptionKey: mapKey,
      },
    });

    mapInstanceRef.current = map;

    map.events.add('ready', () => {
      setMapReady(true);

      // If editing and has existing polygon, display it
      const existingPolygon = initialPolygonRef.current;
      if (existingPolygon && existingPolygon.coordinates) {
        const dataSource = new atlas.source.DataSource();
        map.sources.add(dataSource);

        const polygon = new atlas.data.Feature(
          new atlas.data.Polygon(existingPolygon.coordinates)
        );
        dataSource.add(polygon);

        const polygonLayer = new atlas.layer.PolygonLayer(dataSource, null, {
          fillColor: 'rgba(0, 200, 200, 0.5)',
        });
        const lineLayer = new atlas.layer.LineLayer(dataSource, null, {
          strokeColor: '#007bff',
          strokeWidth: 2,
        });
        map.layers.add([polygonLayer, lineLayer]);

        // Zoom to the existing polygon
        const bbox = atlas.data.BoundingBox.fromData(polygon);
        map.setCamera({ bounds: bbox, padding: 50 });
      }

      try {
        // Create drawing toolbar using CDN-loaded atlas
        const toolbar = new atlas.control.DrawingToolbar({
          buttons: ['draw-polygon', 'edit-geometry', 'erase-geometry'],
          position: 'top-right',
          style: 'light',
        });

        // Create drawing manager with toolbar
        const drawingManager = new atlas.drawing.DrawingManager(map, {
          toolbar: toolbar,
        });

        drawingManagerRef.current = drawingManager;

        // Listen for shape creation/editing
        map.events.add('drawingcomplete', drawingManager, (shape) => {
          const geoJson = shape.toJson();
          setFormData((prev) => ({ ...prev, geolocation_polygon: geoJson.geometry }));
        });
      } catch (err) {
        console.error('Error initializing drawing tools:', err);
      }
    });
  };

  // Cleanup map on unmount
  useEffect(() => {
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.dispose();
        mapInstanceRef.current = null;
      }
    };
  }, []);

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
                  id="site-name"
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
                  id="site-type"
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
                  Site Location - {client?.country ? `${client.country}` : 'Loading...'}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Use the polygon tool in the top-right corner to draw the site boundary on the map
                </Typography>
                <Box
                  id="azureMap"
                  ref={mapContainerRef}
                  sx={{
                    width: '100%',
                    height: 500,
                    border: '1px solid #ccc',
                    borderRadius: 1,
                    bgcolor: mapReady ? 'transparent' : 'grey.100',
                  }}
                >
                  {!mapReady && (
                    <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                      <CircularProgress />
                    </Box>
                  )}
                </Box>
                {formData.geolocation_polygon && (
                  <Typography variant="caption" color="success.main" sx={{ mt: 1, display: 'block' }}>
                    Polygon captured successfully
                  </Typography>
                )}
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
