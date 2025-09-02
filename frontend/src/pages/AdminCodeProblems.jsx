import React from 'react';
import useAuthStore from '../stores/authStore';
import CodeProblemManagement from '../components/CodeProblemManagement';

const AdminCodeProblems = () => {
  const { user } = useAuthStore();

  // 권한 확인
  if (!user || (user.role !== 'admin' && user.role !== 'teacher')) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">접근 권한이 없습니다</h2>
          <p className="text-gray-600">관리자 또는 교사 권한이 필요합니다.</p>
        </div>
      </div>
    );
  }

  return <CodeProblemManagement />;
};

export default AdminCodeProblems;
