import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  IconButton,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Avatar,
  useTheme,
  Tabs,
  Tab,
} from '@mui/material';
import {
  People as PeopleIcon,
  PostAdd as PostIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Dashboard as DashboardIcon,
  Language as LanguageIcon,
} from '@mui/icons-material';
import { MetricsCard } from '../dashboard/MetricsCard';
import { useAppDispatch } from '../../store';
import { api } from '../../services/api';
import { TranslationEditor } from './TranslationEditor';

interface AdminStats {
  totalClients: number;
  activeClients: number;
  totalPosts: number;
  todayPosts: number;
  systemHealth: {
    api: 'healthy' | 'degraded' | 'down';
    database: 'healthy' | 'degraded' | 'down';
    scheduler: 'healthy' | 'degraded' | 'down';
  };
  recentClients: Array<{
    id: string;
    name: string;
    email: string;
    plan: string;
    status: 'active' | 'inactive' | 'suspended';
    lastActive: string;
  }>;
}

export const AdminDashboard: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [stats, setStats] = useState<AdminStats>({
    totalClients: 0,
    activeClients: 0,
    totalPosts: 0,
    todayPosts: 0,
    systemHealth: {
      api: 'healthy',
      database: 'healthy',
      scheduler: 'healthy',
    },
    recentClients: [],
  });

  const fetchAdminStats = async () => {
    try {
      setRefreshing(true);
      const response = await api.get('/api/admin/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching admin stats:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAdminStats();
    // Refresh every 30 seconds
    const interval = setInterval(fetchAdminStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return theme.palette.success.main;
      case 'degraded':
        return theme.palette.warning.main;
      case 'down':
        return theme.palette.error.main;
      default:
        return theme.palette.grey[500];
    }
  };

  const getStatusChip = (status: string) => {
    const color = status === 'active' ? 'success' : status === 'inactive' ? 'warning' : 'error';
    return <Chip label={status} color={color} size="small" />;
  };

  if (loading) return <LinearProgress />;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Admin Dashboard
        </Typography>
        {activeTab === 0 && (
          <IconButton onClick={fetchAdminStats} disabled={refreshing}>
            <RefreshIcon />
          </IconButton>
        )}
      </Box>

      <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value)} sx={{ mb: 3 }}>
        <Tab icon={<DashboardIcon />} label="Overview" iconPosition="start" />
        <Tab icon={<LanguageIcon />} label="Translations" iconPosition="start" />
      </Tabs>

      {activeTab === 0 && (
        <>
          {/* Key Metrics */}
          <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Total Clients"
            value={stats.totalClients}
            trend={12}
            icon={<PeopleIcon />}
            color={theme.palette.primary.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Active Clients"
            value={stats.activeClients}
            trend={8}
            icon={<TrendingUpIcon />}
            color={theme.palette.success.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Total Posts"
            value={stats.totalPosts}
            trend={15}
            icon={<PostIcon />}
            color={theme.palette.info.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Today's Posts"
            value={stats.todayPosts}
            trend={25}
            icon={<PostIcon />}
            color={theme.palette.warning.main}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* System Health */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="System Health"
              action={
                <IconButton size="small">
                  <MoreVertIcon />
                </IconButton>
              }
            />
            <CardContent>
              <Box display="flex" flexDirection="column" gap={2}>
                {Object.entries(stats.systemHealth).map(([service, status]) => (
                  <Box key={service} display="flex" alignItems="center" justifyContent="space-between">
                    <Typography variant="body1" textTransform="capitalize">
                      {service}
                    </Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        width={12}
                        height={12}
                        borderRadius="50%"
                        bgcolor={getHealthColor(status)}
                      />
                      <Typography variant="body2" color={getHealthColor(status)}>
                        {status}
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
              <Box mt={3}>
                <Button variant="outlined" fullWidth>
                  View System Logs
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader title="Quick Actions" />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Button variant="contained" fullWidth startIcon={<PeopleIcon />}>
                    Add New Client
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button variant="outlined" fullWidth>
                    View All Clients
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button variant="outlined" fullWidth>
                    Platform Settings
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button variant="outlined" fullWidth>
                    Export Reports
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Clients */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Recent Clients"
              action={
                <Button size="small" color="primary">
                  View All
                </Button>
              }
            />
            <CardContent>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Client</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Plan</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Last Active</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {stats.recentClients.map((client) => (
                      <TableRow key={client.id}>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            <Avatar sx={{ width: 32, height: 32 }}>
                              {client.name.charAt(0)}
                            </Avatar>
                            <Typography variant="body2">{client.name}</Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{client.email}</TableCell>
                        <TableCell>
                          <Chip label={client.plan} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell>{getStatusChip(client.status)}</TableCell>
                        <TableCell>{new Date(client.lastActive).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <IconButton size="small">
                            <MoreVertIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
        </>
      )}

      {activeTab === 1 && <TranslationEditor />}
    </Box>
  );
};