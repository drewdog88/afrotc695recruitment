import React from 'react';
import { User } from 'lucide-react';

const Profile = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your account settings and profile information
        </p>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="text-center py-12">
            <User className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">User Profile</h3>
            <p className="mt-1 text-sm text-gray-500">
              This section will allow you to view and update your profile information and account settings.
            </p>
            <div className="mt-6">
              <div className="text-sm text-gray-500">
                <p>Features coming soon:</p>
                <ul className="mt-2 space-y-1">
                  <li>• View profile information</li>
                  <li>• Change password</li>
                  <li>• Update account settings</li>
                  <li>• View login history</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile; 