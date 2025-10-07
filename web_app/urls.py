


from django.urls import path
from .views import *

urlpatterns = [
    

 path('all-employee-list/',EmployeeListAPI.as_view(),name='all-employee-list'),
 path('add-project/',AddProjectApi.as_view(),name='add-project'),
 path('list-all-projects/',ListProjectsApi.as_view(),name='list-all-projects'),
 path('teamleaders/', TeamLeaderListAPIView.as_view(), name='teamleader-list'),
 path('projectmanager/', ProjectmanagerListAPIView.as_view(), name='projectmanager-list'),
 path('employee/', EmployeeListAPIView.as_view(), name='employee-list'),
 path('leave-accept/', LeaveAcceptAPI.as_view(), name='leave-accept'),
 path('leave-reject/', LeaveRejectAPI.as_view(), name='leave-reject'),
 path('adminprofile/', AdminProfileView.as_view(), name='admin-profile'),
 path('birthdaystoday/', TodayBirthdayAPIView.as_view(), name='birthdays-today'),
 path('birthdaystomorrow/', TomorrowBirthdayAPIView.as_view(), name='birthdays-tomorrow'),
 path('birthdaysupcoming/', UpcomingBirthdayAPIView.as_view(), name='birthdays-upcoming'),
 path("attendance-summary/", AttendanceSummaryView.as_view(), name="attendance-summary"),
 path("employeesadminview/", EmployeeListadminView.as_view(), name="employee-listadminview"),
 path("employeesfilter-by-designation/", EmployeeListAdminFilteredView.as_view(), name="employee-list-admin"),
 path('employee-designation-counts/',EmployeeCountByDesignation.as_view(),name='employee-designation-counts'),
 path('todays-attendance-count/',TodaysAttendanceCount.as_view(),name='todays-attendance-count'),
 path("employeesdetails/<int:employee_id>/", EmployeeAttendanceView.as_view(), name="employee-attendance"),
# path( "employeedetailwithleave/<int:employee_id>/", Employeedetailswithleave.as_view(), name="employee-details-with-leave"),
path("employee-detail-with-leave/<int:pk>/", EmployeeDetailWithLeave.as_view(), name="employee-detail-with-leave"),
 path("holidayscreate/", HolidayCreateView.as_view(), name="holiday-create"),
  path('holidayslist/', HolidayListView.as_view(), name='holiday-list'),
  path('birthdaystodaywish/', TodayBirthdaywishAPIView.as_view(), name='birthdays-todaywish'),
  path('birthdaystodaywishid/<int:pk>/', TodayBirthdayWishidAPIView.as_view(), name='birthday-wish-by-id'),
  path("employeesactivity/", EmployeeActivityListAPIView.as_view(), name="employeeActivity-list"),
  path('employee-remove/', RemoveEmployeeAPIView.as_view(), name='employee-remove'),
path('employee-reactivate/', ReactivateEmployeeAPIView.as_view(), name='employee-reactivate'),
path('update-project/<int:pk>/',UpdateProjectApi.as_view(),name='update-project'),

path('inactive-employees-list/',InactiveEmployeeListAPIView.as_view(),name='inactive-employees-list'),
path('active-employees-list/',ActiveEmployeeListAPIView.as_view(),name='active-employees-list'),
path('notificationsuser/<int:user_id>/', NotificationLogByUserAPIView.as_view(), name='user-notifications'),
path('projectscount/', ProjectCountAPIView.as_view(), name='project-count'),
path('taskcount/', TaskCountAPIView.as_view(), name='task-count'),
path('add-tasks-to-project/',AddTasksToProjectApi.as_view(),name='add-tasks-to-project'),
path('update-task/<int:task_id>/',EditTaskApi.as_view(),name='update-task'),
path('delete-task/<int:task_id>/',DeleteTaskApi.as_view(),name='delete-task'),

path("attendanceedit/<int:pk>/", AttendanceEditView.as_view(), name="attendance-update"),
path("projectsdelete/<int:project_id>/", DeleteProjectApi.as_view(), name="delete-project"),
path('list-all-tasks/',TaskListAPIView.as_view(),name='list-all-tasks'),
path('taskslast-7-days/', Last7DaysTasksAPIView.as_view(), name='tasks-last-7-days'),
path("taskliststatusfilter/<str:status_filter>/", TaskStatusFilterAPIView.as_view(), name="task-status-filter"),
path('project-detailsneww/<int:project_id>/', ProjectDetailnewwAPIView.as_view(), name='project-detailneww'),
path('update-notificationlog/<int:pk>/', NotificationLogEditAPIView.as_view(), name='update-notificationlog'),
path('pending-approval-count/',DashboardPendingApprovalsCountView.as_view(),name='pending-approval-count'),



]     