import React from 'react';
import { Calendar as CalendarIcon } from 'lucide-react';

const Calendar = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Recruitment Calendar</h1>
        <p className="mt-1 text-sm text-gray-500">
          Schedule and manage recruitment events and activities
        </p>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="text-center py-12">
            <CalendarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Recruitment Calendar</h3>
            <p className="mt-1 text-sm text-gray-500">
              This section will allow you to schedule recruitment events, track event details, and manage your recruitment calendar.
            </p>
            <div className="mt-6">
              <div className="text-sm text-gray-500">
                <p>Features coming soon:</p>
                <ul className="mt-2 space-y-1">
                  <li>• Schedule recruitment events</li>
                  <li>• Track event details and attendees</li>
                  <li>• Calendar view of events</li>
                  <li>• Event status management</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Calendar; 