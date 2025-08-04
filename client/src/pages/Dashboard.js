import React from 'react';
import { Link } from 'react-router-dom';
import { Users, UserCheck, Phone, Calendar, TrendingUp, Shield } from 'lucide-react';

const Dashboard = () => {
  const stats = [
    {
      name: 'Potential Recruits',
      value: '0',
      change: '+0%',
      changeType: 'increase',
      href: '/recruits',
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      name: 'Active Cadre',
      value: '0',
      change: '+0%',
      changeType: 'increase',
      href: '/cadre',
      icon: UserCheck,
      color: 'bg-green-500',
    },
    {
      name: 'University Contacts',
      value: '0',
      change: '+0%',
      changeType: 'increase',
      href: '/contacts',
      icon: Phone,
      color: 'bg-purple-500',
    },
    {
      name: 'Upcoming Events',
      value: '0',
      change: '+0%',
      changeType: 'increase',
      href: '/calendar',
      icon: Calendar,
      color: 'bg-orange-500',
    },
  ];

  const quickActions = [
    {
      name: 'Add New Recruit',
      description: 'Add a potential recruit to the system',
      href: '/recruits',
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      name: 'Add Cadre Member',
      description: 'Add a new cadre member',
      href: '/cadre',
      icon: UserCheck,
      color: 'bg-green-500',
    },
    {
      name: 'Add Contact',
      description: 'Add a university contact',
      href: '/contacts',
      icon: Phone,
      color: 'bg-purple-500',
    },
    {
      name: 'Schedule Event',
      description: 'Schedule a recruitment event',
      href: '/calendar',
      icon: Calendar,
      color: 'bg-orange-500',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome to AFROTC 695 Recruitment Management System
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <div key={item.name} className="card">
            <div className="card-body">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className={`${item.color} rounded-md p-3`}>
                    <item.icon className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {item.name}
                    </dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">
                        {item.value}
                      </div>
                      <div className="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                        <TrendingUp className="self-center flex-shrink-0 h-4 w-4 text-green-500" />
                        <span className="sr-only">{item.changeType}</span>
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
              <div className="mt-4">
                <Link
                  to={item.href}
                  className="text-sm font-medium text-primary-600 hover:text-primary-500"
                >
                  View all
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
          <p className="mt-1 text-sm text-gray-500">
            Common tasks to help you get started
          </p>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {quickActions.map((action) => (
              <Link
                key={action.name}
                to={action.href}
                className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
              >
                <div>
                  <span className={`${action.color} rounded-lg inline-flex p-3 ring-4 ring-white`}>
                    <action.icon className="h-6 w-6 text-white" />
                  </span>
                </div>
                <div className="mt-4">
                  <h3 className="text-lg font-medium text-gray-900 group-hover:text-primary-600">
                    {action.name}
                  </h3>
                  <p className="mt-2 text-sm text-gray-500">
                    {action.description}
                  </p>
                </div>
                <span
                  className="absolute top-6 right-6 text-gray-300 group-hover:text-gray-400"
                  aria-hidden="true"
                >
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0h-2zM8 3a1 1 0 000 2V3zM3.293 19.293a1 1 0 101.414 1.414l-1.414-1.414zM19 4v12h2V4h-2zm1-1H8v2h12V3zm-.707.293l-16 16 1.414 1.414 16-16-1.414-1.414z" />
                  </svg>
                </span>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Welcome Message */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Shield className="h-12 w-12 text-primary-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">
                Welcome to AFROTC 695 Recruitment Management
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                This system helps you track potential recruits, manage cadre, coordinate with university contacts, 
                and schedule recruitment events. Use the navigation menu to access different sections of the system.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 