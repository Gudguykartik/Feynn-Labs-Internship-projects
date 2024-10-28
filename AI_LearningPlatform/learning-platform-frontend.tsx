import { useState, useEffect } from 'react';
import { Layout, BookOpen, Award, Activity, User } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000';

// Mock user for demo purposes
const DEMO_USER = {
  id: 'user1',
  name: 'John Doe',
  interests: 'programming, AI, web development',
  learning_style: 'visual'
};

const Dashboard = () => {
  const [courses, setCourses] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [coursesRes, recommendationsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/courses`),
          fetch(`${API_BASE_URL}/users/${DEMO_USER.id}/recommendations`)
        ]);
        
        const coursesData = await coursesRes.json();
        const recommendationsData = await recommendationsRes.json();
        
        setCourses(coursesData.courses);
        setRecommendations(recommendationsData.recommendations);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const updateProgress = async (courseId, moduleId, progress) => {
    try {
      await fetch(`${API_BASE_URL}/users/${DEMO_USER.id}/progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          course_id: courseId,
          module_id: moduleId,
          progress,
        }),
      });
      
      // Refresh recommendations after progress update
      const response = await fetch(`${API_BASE_URL}/users/${DEMO_USER.id}/recommendations`);
      const data = await response.json();
      setRecommendations(data.recommendations);
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <Layout className="h-8 w-8 text-blue-600 mr-2" />
              <h1 className="text-2xl font-bold text-gray-900">AI Learning Platform</h1>
            </div>
            <div className="flex items-center space-x-4">
              <User className="h-6 w-6 text-gray-600" />
              <span className="text-gray-700">{DEMO_USER.name}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-3 py-4 text-sm font-medium ${
                activeTab === 'dashboard'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab('courses')}
              className={`px-3 py-4 text-sm font-medium ${
                activeTab === 'courses'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              All Courses
            </button>
            <button
              onClick={() => setActiveTab('progress')}
              className={`px-3 py-4 text-sm font-medium ${
                activeTab === 'progress'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              My Progress
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <>
            {activeTab === 'dashboard' && (
              <div className="space-y-6">
                {/* Recommendations Section */}
                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    Recommended for You
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {recommendations.map((course) => (
                      <div
                        key={course.id}
                        className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="text-lg font-medium text-gray-900">
                              {course.name}
                            </h3>
                            <p className="mt-1 text-sm text-gray-500">
                              {course.description}
                            </p>
                          </div>
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {course.difficulty}
                          </span>
                        </div>
                        <div className="mt-4">
                          <div className="flex items-center">
                            <div className="flex-1">
                              <div className="bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-blue-600 rounded-full h-2"
                                  style={{ width: `${course.progress || 0}%` }}
                                ></div>
                              </div>
                            </div>
                            <span className="ml-2 text-sm text-gray-500">
                              {course.progress || 0}%
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                {/* Quick Stats */}
                <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <BookOpen className="h-6 w-6 text-blue-600" />
                      <h3 className="ml-2 text-lg font-medium text-gray-900">
                        Active Courses
                      </h3>
                    </div>
                    <p className="mt-2 text-3xl font-semibold text-gray-900">
                      {recommendations.length}
                    </p>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <Activity className="h-6 w-6 text-green-600" />
                      <h3 className="ml-2 text-lg font-medium text-gray-900">
                        Average Progress
                      </h3>
                    </div>
                    <p className="mt-2 text-3xl font-semibold text-gray-900">
                      {Math.round(
                        recommendations.reduce((acc, course) => acc + (course.progress || 0), 0) /
                          recommendations.length || 0
                      )}%
                    </p>
                  </div>
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                      <Award className="h-6 w-6 text-yellow-600" />
                      <h3 className="ml-2 text-lg font-medium text-gray-900">
                        Completed Modules
                      </h3>
                    </div>
                    <p className="mt-2 text-3xl font-semibold text-gray-900">
                      {recommendations.reduce(
                        (acc, course) =>
                          acc + (course.progress === 100 ? course.modules?.length || 0 : 0),
                        0
                      )}
                    </p>
                  </div>
                </section>
              </div>
            )}

            {activeTab === 'courses' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">All Courses</h2>
                <div className="grid grid-cols-1 gap-6">
                  {courses.map((course) => (
                    <div
                      key={course.id}
                      className="bg-white rounded-lg shadow p-6"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">
                            {course.name}
                          </h3>
                          <p className="mt-1 text-sm text-gray-500">
                            {course.description}
                          </p>
                        </div>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {course.difficulty}
                        </span>
                      </div>
                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-gray-900">Modules</h4>
                        <ul className="mt-2 space-y-3">
                          {course.modules.map((module) => (
                            <li
                              key={module.id}
                              className="flex items-center justify-between text-sm"
                            >
                              <span className="text-gray-600">{module.title}</span>
                              <span className="text-gray-500">{module.duration} min</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'progress' && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold text-gray-900">My Progress</h2>
                <div className="grid grid-cols-1 gap-6">
                  {recommendations.map((course) => (
                    <div
                      key={course.id}
                      className="bg-white rounded-lg shadow p-6"
                    >
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-medium text-gray-900">
                          {course.name}
                        </h3>
                        <span className="text-sm text-gray-500">
                          Overall Progress: {course.progress || 0}%
                        </span>
                      </div>
                      <div className="mt-4 space-y-4">
                        {course.modules.map((module) => (
                          <div key={module.id} className="space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium text-gray-900">
                                {module.title}
                              </span>
                              <button
                                onClick={() => updateProgress(course.id, module.id, 100)}
                                className="px-3 py-1 text-sm text-white bg-blue-600 rounded hover:bg-blue-700"
                              >
                                Mark Complete
                              </button>
                            </div>
                            <div className="flex items-center">
                              <div className="flex-1">
                                <div className="bg-gray-200 rounded-full h-2">
                                  <div
                                    className="bg-blue-600 rounded-full h-2"
                                    style={{
                                      width: `${
                                        course.progress
                                          ? (course.progress * module.duration) / 100
                                          : 0
                                      }%`,
                                    }}
                                  ></div>
                                </div>
                              </div>
                              <span className="ml-2 text-sm text-gray-500">
                                {module.duration} min
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
