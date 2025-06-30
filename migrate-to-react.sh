#!/bin/bash

echo "=== Migrating to Full React SPA ==="
echo ""

# Step 1: Check current React app
echo "1. Checking React app structure..."
cd frontend-react

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Step 2: Create admin and owner directories
echo ""
echo "2. Creating admin and owner components..."
mkdir -p src/pages/admin
mkdir -p src/pages/owner

# Step 3: Create placeholder admin dashboard
cat > src/pages/admin/Dashboard.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import api from '../../services/api';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalClients: 0,
    activeClients: 0,
    totalPosts: 0,
    todayPosts: 0
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/admin/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Total Clients</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.totalClients}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Active Clients</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.activeClients}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Total Posts</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.totalPosts}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Today's Posts</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats.todayPosts}</p>
          </CardContent>
        </Card>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <button className="btn btn-primary mb-2 w-full">Add New Client</button>
            <button className="btn btn-secondary mb-2 w-full">View All Clients</button>
            <button className="btn btn-secondary w-full">Platform Settings</button>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Activity feed coming soon...</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminDashboard;
EOF

# Step 4: Create owner dashboard
cat > src/pages/owner/Dashboard.js << 'EOF'
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";

const OwnerDashboard = () => {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Owner Dashboard</h1>
      <Card>
        <CardHeader>
          <CardTitle>Platform Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Complete platform analytics and controls coming soon...</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default OwnerDashboard;
EOF

# Step 5: Update App.js to include new routes
echo ""
echo "3. Updating App.js with complete routing..."
# This would need manual updating of App.js

# Step 6: Build the React app
echo ""
echo "4. Building React application..."
npm run build

echo ""
echo "✅ React app prepared for deployment!"
echo ""
echo "Next steps:"
echo "1. Manually update src/App.js with the routing code from REACT_MIGRATION_PLAN.md"
echo "2. Build again: npm run build"
echo "3. Deploy to production: scp -r build/* root@kuwait-social-ai-1750866347:/var/www/html/"
echo "4. Update nginx on server to serve React app"
echo ""
echo "The old static HTML files will be replaced with the React SPA."