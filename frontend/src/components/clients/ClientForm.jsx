import React, { useState, useEffect } from 'react';
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
  MenuItem,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import clientService from '../../services/clientService';

const ORGANIZATION_SIZES = ['1-10', '11-50', '51-200', '201-500', '501-1000', '1000+'];

function ClientForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = Boolean(id);

  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    country: '',
    business_type: '',
    organization_size: '',
  });
  const [errors, setErrors] = useState({});
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    if (isEdit) {
      loadClient();
    }
  }, [id]);

  const loadClient = async () => {
    try {
      setLoading(true);
      const data = await clientService.getClient(id);
      setFormData({
        name: data.name,
        country: data.country,
        business_type: data.business_type,
        organization_size: data.organization_size,
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to load client',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field) => (event) => {
    setFormData({ ...formData, [field]: event.target.value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: null });
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = 'Client name is required';
    if (!formData.country.trim()) newErrors.country = 'Country is required';
    if (!formData.business_type.trim()) newErrors.business_type = 'Business type is required';
    if (!formData.organization_size) newErrors.organization_size = 'Organization size is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      setSaving(true);
      if (isEdit) {
        await clientService.updateClient(id, formData);
        setSnackbar({
          open: true,
          message: 'Client updated successfully',
          severity: 'success',
        });
      } else {
        await clientService.createClient(formData);
        setSnackbar({
          open: true,
          message: 'Client created successfully',
          severity: 'success',
        });
      }
      setTimeout(() => navigate('/clients'), 1500);
    } catch (error) {
      setSnackbar({
        open: true,
        message: `Failed to ${isEdit ? 'update' : 'create'} client`,
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
        {isEdit ? 'Edit Client' : 'Add New Client'}
      </Typography>

      <Card>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Client Name"
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
                  label="Country"
                  value={formData.country}
                  onChange={handleChange('country')}
                  error={Boolean(errors.country)}
                  helperText={errors.country}
                  required
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Business Type"
                  value={formData.business_type}
                  onChange={handleChange('business_type')}
                  error={Boolean(errors.business_type)}
                  helperText={errors.business_type}
                  required
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  select
                  label="Organization Size"
                  value={formData.organization_size}
                  onChange={handleChange('organization_size')}
                  error={Boolean(errors.organization_size)}
                  helperText={errors.organization_size}
                  required
                >
                  {ORGANIZATION_SIZES.map((size) => (
                    <MenuItem key={size} value={size}>
                      {size}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>

              <Grid item xs={12}>
                <Box display="flex" gap={2} justifyContent="flex-end">
                  <Button
                    variant="outlined"
                    startIcon={<CancelIcon />}
                    onClick={() => navigate('/clients')}
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

export default ClientForm;
