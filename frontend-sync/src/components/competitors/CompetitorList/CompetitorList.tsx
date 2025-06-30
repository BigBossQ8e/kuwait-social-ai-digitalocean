// Competitor list component with management features

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Button,
  Chip,
  Avatar,
  Menu,
  MenuItem,
  TextField,
  InputAdornment,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  Stack,
  Alert,
  CircularProgress,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Add,
  Search,
  MoreVert,
  Edit,
  Delete,
  Analytics,
  TrendingUp,
  TrendingDown,
  Instagram,
  Twitter,
  CameraAlt,
  Refresh,
  ContentCopy,
  Person,
  Business,
  Close,
  CheckCircle,
  Warning,
} from '@mui/icons-material';
import { format, formatDistanceToNow } from 'date-fns';
import { ar, enUS } from 'date-fns/locale';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import type { Competitor, CompetitorAnalysis } from '../../../types/api.types';

interface CompetitorListProps {
  competitors: Competitor[];
  loading?: boolean;
  error?: string | null;
  onAdd?: (competitor: Omit<Competitor, 'id' | 'created_at'>) => void;
  onEdit?: (competitor: Competitor) => void;
  onDelete?: (competitorId: number) => void;
  onAnalyze?: (competitorId: number) => void;
  onRefresh?: () => void;
}

interface CompetitorFormData {
  name: string;
  username: string;
  platform: string;
  notes?: string;
}

const platformIcons: Record<string, React.ReactNode> = {
  instagram: <Instagram />,
  twitter: <Twitter />,
  snapchat: <CameraAlt />,
};

const platformColors: Record<string, string> = {
  instagram: '#E4405F',
  twitter: '#1DA1F2',
  snapchat: '#FFFC00',
};

export const CompetitorList: React.FC<CompetitorListProps> = ({
  competitors,
  loading = false,
  error = null,
  onAdd,
  onEdit,
  onDelete,
  onAnalyze,
  onRefresh,
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);
  const locale = language === 'ar' ? ar : enUS;

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedCompetitor, setSelectedCompetitor] = useState<Competitor | null>(null);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [formData, setFormData] = useState<CompetitorFormData>({
    name: '',
    username: '',
    platform: 'instagram',
    notes: '',
  });

  const filteredCompetitors = competitors.filter(competitor => {
    const query = searchQuery.toLowerCase();
    return (
      competitor.name.toLowerCase().includes(query) ||
      competitor.username.toLowerCase().includes(query) ||
      competitor.platform.toLowerCase().includes(query) ||
      (competitor.notes && competitor.notes.toLowerCase().includes(query))
    );
  });

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, competitor: Competitor) => {
    setAnchorEl(event.currentTarget);
    setSelectedCompetitor(competitor);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedCompetitor(null);
  };

  const handleAddCompetitor = () => {
    if (onAdd && formData.name && formData.username) {
      onAdd({
        client_id: 1, // This should come from context/props
        name: formData.name,
        username: formData.username,
        platform: formData.platform,
        notes: formData.notes,
        is_active: true,
      });
      setAddDialogOpen(false);
      setFormData({
        name: '',
        username: '',
        platform: 'instagram',
        notes: '',
      });
    }
  };

  const handleEditCompetitor = () => {
    if (selectedCompetitor) {
      setFormData({
        name: selectedCompetitor.name,
        username: selectedCompetitor.username,
        platform: selectedCompetitor.platform,
        notes: selectedCompetitor.notes || '',
      });
      setAddDialogOpen(true);
      handleMenuClose();
    }
  };

  const handleDeleteCompetitor = () => {
    if (selectedCompetitor && onDelete) {
      onDelete(selectedCompetitor.id);
      setDeleteDialogOpen(false);
      handleMenuClose();
    }
  };

  const getEngagementTrend = (analysis?: CompetitorAnalysis) => {
    if (!analysis) return null;
    
    // Mock trend calculation
    const trend = Math.random() > 0.5 ? 'up' : 'down';
    const percentage = Math.floor(Math.random() * 20) + 1;
    
    return (
      <Chip
        size="small"
        icon={trend === 'up' ? <TrendingUp /> : <TrendingDown />}
        label={`${percentage}%`}
        color={trend === 'up' ? 'success' : 'error'}
        sx={{ minWidth: 70 }}
      />
    );
  };

  const getStatusChip = (competitor: Competitor) => {
    const hasRecentAnalysis = competitor.latest_analysis && 
      new Date(competitor.latest_analysis.analysis_date) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
    
    if (!competitor.is_active) {
      return <Chip size="small" label={language === 'ar' ? 'غير نشط' : 'Inactive'} />;
    }
    
    if (hasRecentAnalysis) {
      return (
        <Chip
          size="small"
          icon={<CheckCircle />}
          label={language === 'ar' ? 'محدث' : 'Up to date'}
          color="success"
        />
      );
    }
    
    return (
      <Chip
        size="small"
        icon={<Warning />}
        label={language === 'ar' ? 'يحتاج تحديث' : 'Needs update'}
        color="warning"
      />
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" action={
        onRefresh && (
          <Button color="inherit" size="small" onClick={onRefresh}>
            {language === 'ar' ? 'إعادة المحاولة' : 'Retry'}
          </Button>
        )
      }>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">
          {language === 'ar' ? 'المنافسون' : 'Competitors'}
        </Typography>
        
        <Stack direction="row" spacing={2}>
          {onRefresh && (
            <IconButton onClick={onRefresh}>
              <Refresh />
            </IconButton>
          )}
          {onAdd && (
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setAddDialogOpen(true)}
            >
              {language === 'ar' ? 'إضافة منافس' : 'Add Competitor'}
            </Button>
          )}
        </Stack>
      </Box>

      {/* Search Bar */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          placeholder={language === 'ar' ? 'البحث عن المنافسين...' : 'Search competitors...'}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      {/* Competitors Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{language === 'ar' ? 'المنافس' : 'Competitor'}</TableCell>
              <TableCell>{language === 'ar' ? 'المنصة' : 'Platform'}</TableCell>
              <TableCell align="center">{language === 'ar' ? 'المتابعون' : 'Followers'}</TableCell>
              <TableCell align="center">{language === 'ar' ? 'التفاعل' : 'Engagement'}</TableCell>
              <TableCell align="center">{language === 'ar' ? 'الحالة' : 'Status'}</TableCell>
              <TableCell>{language === 'ar' ? 'آخر تحليل' : 'Last Analysis'}</TableCell>
              <TableCell align="right">{language === 'ar' ? 'الإجراءات' : 'Actions'}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredCompetitors.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                    {searchQuery
                      ? (language === 'ar' ? 'لا توجد نتائج مطابقة' : 'No results found')
                      : (language === 'ar' ? 'لا يوجد منافسون بعد' : 'No competitors yet')
                    }
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredCompetitors
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((competitor) => (
                  <TableRow key={competitor.id} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Avatar sx={{ bgcolor: theme.palette.grey[200] }}>
                          <Business />
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {competitor.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            @{competitor.username}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={platformIcons[competitor.platform] as React.ReactElement}
                        label={competitor.platform}
                        size="small"
                        sx={{
                          backgroundColor: alpha(platformColors[competitor.platform], 0.1),
                          color: platformColors[competitor.platform],
                        }}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Typography variant="body2">
                        {competitor.latest_analysis?.followers_count?.toLocaleString() || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Stack direction="row" spacing={1} justifyContent="center" alignItems="center">
                        <Typography variant="body2">
                          {competitor.latest_analysis?.engagement_rate
                            ? `${competitor.latest_analysis.engagement_rate.toFixed(2)}%`
                            : '-'
                          }
                        </Typography>
                        {getEngagementTrend(competitor.latest_analysis)}
                      </Stack>
                    </TableCell>
                    <TableCell align="center">
                      {getStatusChip(competitor)}
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" color="text.secondary">
                        {competitor.latest_analysis
                          ? formatDistanceToNow(new Date(competitor.latest_analysis.analysis_date), {
                              addSuffix: true,
                              locale,
                            })
                          : language === 'ar' ? 'لم يتم التحليل' : 'Not analyzed'
                        }
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={1} justifyContent="flex-end">
                        {onAnalyze && (
                          <Tooltip title={language === 'ar' ? 'تحليل' : 'Analyze'}>
                            <IconButton
                              size="small"
                              onClick={() => onAnalyze(competitor.id)}
                            >
                              <Analytics />
                            </IconButton>
                          </Tooltip>
                        )}
                        <IconButton
                          size="small"
                          onClick={(e) => handleMenuOpen(e, competitor)}
                        >
                          <MoreVert />
                        </IconButton>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))
            )}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={filteredCompetitors.length}
          page={page}
          onPageChange={(event, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(event) => {
            setRowsPerPage(parseInt(event.target.value, 10));
            setPage(0);
          }}
          labelRowsPerPage={language === 'ar' ? 'عدد الصفوف:' : 'Rows per page:'}
        />
      </TableContainer>

      {/* Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        {onEdit && (
          <MenuItem onClick={handleEditCompetitor}>
            <Edit fontSize="small" sx={{ mr: 1 }} />
            {language === 'ar' ? 'تعديل' : 'Edit'}
          </MenuItem>
        )}
        <MenuItem onClick={() => {
          // Copy username to clipboard
          if (selectedCompetitor) {
            navigator.clipboard.writeText(`@${selectedCompetitor.username}`);
          }
          handleMenuClose();
        }}>
          <ContentCopy fontSize="small" sx={{ mr: 1 }} />
          {language === 'ar' ? 'نسخ المعرف' : 'Copy Username'}
        </MenuItem>
        {onDelete && (
          <MenuItem
            onClick={() => setDeleteDialogOpen(true)}
            sx={{ color: 'error.main' }}
          >
            <Delete fontSize="small" sx={{ mr: 1 }} />
            {language === 'ar' ? 'حذف' : 'Delete'}
          </MenuItem>
        )}
      </Menu>

      {/* Add/Edit Dialog */}
      <Dialog
        open={addDialogOpen}
        onClose={() => {
          setAddDialogOpen(false);
          setFormData({
            name: '',
            username: '',
            platform: 'instagram',
            notes: '',
          });
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              {selectedCompetitor
                ? (language === 'ar' ? 'تعديل المنافس' : 'Edit Competitor')
                : (language === 'ar' ? 'إضافة منافس جديد' : 'Add New Competitor')
              }
            </Typography>
            <IconButton
              onClick={() => setAddDialogOpen(false)}
              size="small"
            >
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label={language === 'ar' ? 'اسم المنافس' : 'Competitor Name'}
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label={language === 'ar' ? 'معرف المستخدم' : 'Username'}
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              fullWidth
              required
              helperText={language === 'ar' ? 'بدون @' : 'Without @'}
              InputProps={{
                startAdornment: <InputAdornment position="start">@</InputAdornment>,
              }}
            />
            <FormControl fullWidth>
              <InputLabel>{language === 'ar' ? 'المنصة' : 'Platform'}</InputLabel>
              <Select
                value={formData.platform}
                onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
                label={language === 'ar' ? 'المنصة' : 'Platform'}
              >
                <MenuItem value="instagram">
                  <Box display="flex" alignItems="center" gap={1}>
                    <Instagram fontSize="small" />
                    Instagram
                  </Box>
                </MenuItem>
                <MenuItem value="twitter">
                  <Box display="flex" alignItems="center" gap={1}>
                    <Twitter fontSize="small" />
                    Twitter
                  </Box>
                </MenuItem>
                <MenuItem value="snapchat">
                  <Box display="flex" alignItems="center" gap={1}>
                    <CameraAlt fontSize="small" />
                    Snapchat
                  </Box>
                </MenuItem>
              </Select>
            </FormControl>
            <TextField
              label={language === 'ar' ? 'ملاحظات' : 'Notes'}
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              fullWidth
              multiline
              rows={3}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>
            {language === 'ar' ? 'إلغاء' : 'Cancel'}
          </Button>
          <Button
            variant="contained"
            onClick={handleAddCompetitor}
            disabled={!formData.name || !formData.username}
          >
            {selectedCompetitor
              ? (language === 'ar' ? 'حفظ التغييرات' : 'Save Changes')
              : (language === 'ar' ? 'إضافة' : 'Add')
            }
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>
          {language === 'ar' ? 'تأكيد الحذف' : 'Confirm Delete'}
        </DialogTitle>
        <DialogContent>
          <Typography>
            {language === 'ar'
              ? `هل أنت متأكد من حذف "${selectedCompetitor?.name}"؟`
              : `Are you sure you want to delete "${selectedCompetitor?.name}"?`
            }
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            {language === 'ar' ? 'إلغاء' : 'Cancel'}
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleDeleteCompetitor}
          >
            {language === 'ar' ? 'حذف' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};