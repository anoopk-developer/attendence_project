from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from .models import *
from web_app.serializers import* 


# -----------------------------
# User Login Serializer
# -----------------------------
class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
        }


# -----------------------------
# Bank Detail Serializer
# -----------------------------
class BankDetailSerializer(serializers.ModelSerializer):
    accountNumber = serializers.CharField(source="account_number")
    ifscCode = serializers.CharField(source="ifsc_code")
    branchName = serializers.CharField(source="branch_name")
    accountHolder = serializers.CharField(source="account_holder")

    class Meta:
        model = BankDetail
        fields = [
            "id", "accountNumber", "ifscCode", "branchName",
            "accountHolder", "documents", "created_at", "updated_at"
        ]


# -----------------------------
# Employee Serializer
# -----------------------------
# -----------------------------
# Employee Serializer
# -----------------------------
# -----------------------------
# Employee Serializer
# -----------------------------
class EmployeeSerializer(serializers.ModelSerializer):
    # CamelCase mapping
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    employeeId = serializers.CharField(source="employee_id")

    # Manager now stored as plain text
    repMgrTl = serializers.CharField(
        source="reporting_manager",
        required=False,
        allow_blank=True,
        allow_null=True
    )

    confirmPassword = serializers.CharField(write_only=True, required=True)

    # Email & password for linked User
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    # Bank fields
    accountNumber = serializers.CharField(write_only=True, required=False)
    confirmAccountNumber = serializers.CharField(write_only=True, required=False)
    ifscCode = serializers.CharField(write_only=True, required=False)
    branchName = serializers.CharField(write_only=True, required=False)
    accountHolderName = serializers.CharField(write_only=True, required=False)
    documents = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )


    # Profile picture
    profile_pic = serializers.ImageField(required=False)

    class Meta:
        model = EmployeeDetail
        fields = [
            "id", "firstName", "lastName", "employeeId",
            "department", "designation", "repMgrTl", "is_team_lead",
            "salary", "email", "password", "confirmPassword",
            "profile_pic", "phone", "address", "dob","user_type","job_type",
            "gender", "nationality", "blood_group", "emergency_contact",
            # Bank fields
            "accountNumber", "confirmAccountNumber", "ifscCode",
            "branchName", "accountHolderName", "documents","company_branch",
        ]

    def validate(self, data):
        if data["password"] != data["confirmPassword"]:
            raise serializers.ValidationError("Passwords do not match")
        if data.get("accountNumber") and data.get("accountNumber") != data.get("confirmAccountNumber"):
            raise serializers.ValidationError("Account numbers do not match")
        validate_email(data["email"])
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        logged_in_user = request.user if request else None

        validated_data.pop("confirmPassword", None)
        raw_password = validated_data.pop("password")
        email = validated_data.pop("email")

        account_number = validated_data.pop("accountNumber", None)
        validated_data.pop("confirmAccountNumber", None)
        ifsc_code = validated_data.pop("ifscCode", None)
        branch_name = validated_data.pop("branchName", None)
        account_holder = validated_data.pop("accountHolderName", None)
        documents_files = validated_data.pop("documents", [])
        profile_pic_file = validated_data.pop("profile_pic", None)

        if profile_pic_file:
            validated_data["profile_pic"] = profile_pic_file

        # ---------------------------------
        # Determine role based on conditions
        # ---------------------------------
        user_type = validated_data.get("user_type", "").strip().lower()

        if logged_in_user and logged_in_user.role == "superadmin":
            user_role = "admin"  # ✅ Superadmin creates admins
            # Assign company_branch from data if provided
            company_branch = validated_data.get("company_branch")
            validated_data["company_branch"] = company_branch
        elif user_type in ["admin management", "admin team lead", "team lead", "team leader"]:
            user_role = "admin"
        else:
            user_role = "employee"

        # Create linked User
        user = User.objects.create(
            email=email,
            role=user_role,
            password=make_password(raw_password),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )

        # Create EmployeeDetail
        employee = EmployeeDetail.objects.create(user=user, **validated_data)

        # Create BankDetail if provided
        if account_number:
            bank_detail = BankDetail.objects.create(
                employee=employee,
                account_number=account_number,
                ifsc_code=ifsc_code,
                branch_name=branch_name,
                account_holder=account_holder,
            )
            for doc in documents_files:
                bank_detail.documents.save(doc.name, doc, save=True)

        return employee
    
  
  
  
  
    
    
    
class EmployeeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDetail
        fields = [
            "id",
            "employee_id",
            "first_name",
            "last_name",
            "department",
            "designation",
            "reporting_manager",
            "is_team_lead",
            "salary",
            "profile_pic",
            "phone",
            "address",
            "dob",
            "gender",
            "nationality",
            "blood_group",
            "emergency_contact",
            "created_at",
            "updated_at",
        ]

# attendance serializer
class AttendanceSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "date",
            "in_time",
            "out_time",
            "attendance_type",
            "location",
             "latitude",       # ✅ instead of location
            "longitude", 
            "qr_scan",
            "selfie",
            "status",
            "verified_by",
            "created_at",
            "updated_at",
            "punch_in",
        ]

    def get_latitude(self, obj):
        if obj.qrsession:
            return obj.qrsession.latitudes
        return None

    def get_longitude(self, obj):
        if obj.qrsession:
            return obj.qrsession.longitude
        return None    


#  leave serializer
class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = [
            "id",
            "user",
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "status",
            "approved_by",
            "attachments",
            "reason",
        ]

# project serializer



# project , task , members  serializer

class TaskSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = Task
        fields = ["id","title", "description", "assigned_by", "assigned_to", "status"]

from django.utils.timezone import make_naive
from django.utils.timezone import now, make_naive
from rest_framework import serializers
from .models import Task

class TaskReadSerializer(serializers.ModelSerializer):
    assigned_by_id = serializers.IntegerField(source="assigned_by.id", read_only=True)
    assigned_by_name = serializers.SerializerMethodField()
    assigned_to_id = serializers.IntegerField(source="assigned_to.id", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    task_hours = serializers.SerializerMethodField()           # total hours
    current_progress = serializers.SerializerMethodField()     # current spent / total hours

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "assigned_by_id",
            "assigned_by_name",
            "assigned_to_id",
            "assigned_to_name",
            "created_at",
            "updated_at",
            "due_date",
            "task_hours",
            "current_progress",
        ]

    def get_assigned_by_name(self, obj):
        return obj.assigned_by.email if obj.assigned_by else None

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.email if obj.assigned_to else None

    def get_task_hours(self, obj):
        """Total available hours between created_at and due_date."""
        if obj.created_at and obj.due_date:
            start = make_naive(obj.created_at)
            end = make_naive(obj.due_date)
            delta = end - start
            return round(delta.total_seconds() / 3600, 2)
        return None

    def get_current_progress(self, obj):
        """Fraction value of hours spent so far / total hours."""
        if obj.created_at and obj.due_date:
            start = make_naive(obj.created_at)
            end = make_naive(obj.due_date)
            total_seconds = (end - start).total_seconds()
            elapsed_seconds = (make_naive(now()) - start).total_seconds()

            # Avoid negative values or division by zero
            if total_seconds <= 0:
                return 0.0

            progress_fraction = elapsed_seconds / total_seconds
            # Clamp to 1.0 max
            progress_fraction = max(0.0, min(progress_fraction, 1.0))

            # Return formatted as "x.xx / total_hours"
            total_hours = round(total_seconds / 3600, 2)
            current_hours = round(elapsed_seconds / 3600, 2)
            return f"{current_hours} / {total_hours} hours ({round(progress_fraction*100, 1)}%)"

        return None



class TaskWithProjectSerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    project_details = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "assigned_by_name",
            "assigned_to_name",
            "created_at",
            "updated_at",
            "project_details",
        ]

    def get_assigned_by_name(self, obj):
        if obj.assigned_by and obj.assigned_by.employee_profile:
            return f"{obj.assigned_by.employee_profile.first_name} {obj.assigned_by.employee_profile.last_name}"
        return obj.assigned_by.email if obj.assigned_by else None

    def get_assigned_to_name(self, obj):
        if obj.assigned_to and obj.assigned_to.employee_profile:
            return f"{obj.assigned_to.employee_profile.first_name} {obj.assigned_to.employee_profile.last_name}"
        return obj.assigned_to.email if obj.assigned_to else None

    def get_project_details(self, obj):
        if obj.project:
            return {
                "id": obj.project.id,
                "project_name": obj.project.project_name,
                "client": obj.project.client,
                "start_date": obj.project.start_date,
                "end_date": obj.project.end_date,
                "priority": obj.project.priority,
                "project_value": obj.project.project_value,
                "total_working_hours": obj.project.total_working_hours,
                "extra_time": obj.project.extra_time,
                "description": obj.project.description,
                "status": obj.project.status,
                "project_logo": obj.project.project_logo.url if obj.project.project_logo else None,
                "attachment": obj.project.attachment.url if obj.project.attachment else None,
            }
        return None

class ProjectMembersSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = ProjectMembers
        fields = ["id","team_leader", "project_manager", "tags"]


class ProjectMembersReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMembers
        fields = ["id", "team_leader", "project_manager", "tags"]

class ProjectSerializer(serializers.ModelSerializer):
    members = ProjectMembersSerializer(write_only=True, many=True)  # expects list of dicts
    tasks = TaskSerializer(many=True, write_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "project_logo",
            "project_name",
            "client",
            "start_date",
            "end_date",
            "priority",
            "project_value",
            "total_working_hours",
            "extra_time",
            "description",
            "attachment",
            "members",
            "tasks",
        ]

    def create(self, validated_data):
        members_data = validated_data.pop("members")
        tasks_data = validated_data.pop("tasks")

        # Create Project
        project = Project.objects.create(**validated_data)

        # Create multiple ProjectMembers
        for member in members_data:
            ProjectMembers.objects.create(project=project, **member)

        # Create multiple Tasks
        request = self.context.get("request")
        assigned_by_user = getattr(request, "user", None) if request else None
        for task_data in tasks_data:
            Task.objects.create(
                project=project,
                assigned_by=assigned_by_user,
                **task_data,
            )

        return project


class ProjectReadSerializer(serializers.ModelSerializer):
    members = ProjectMembersReadSerializer(source="projectmembers_set", many=True, read_only=True)
    tasks = TaskReadSerializer(source="task_set", many=True, read_only=True)
    project_images = ProjectImageSerializer(source="images", many=True, read_only=True)
    ptoject_files = ProjectFileSerializer(source="files", many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "project_logo",
            "project_name",
            "client",
            "start_date",
            "end_date",
            "priority",
            "project_value",
            "total_working_hours",
            "extra_time",
            "description",
            "status",
            "reason_for_rejection",
            "attachment",
            "members",
            "tasks",
            "project_images",
            "ptoject_files",
        ]        
        
        
        

class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = [
            "id",
            "user",
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "status",
            "approved_by",
            "attachments",
            "reason",
        ]    
        
        
        
        
class LeaveSerializerview(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    approved_by = serializers.StringRelatedField()

    class Meta:
        model = Leave
        fields = '__all__'    
        
        
        




# attendance serializer
class AttendanceSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    in_time = serializers.SerializerMethodField()
    out_time = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "date",
            "in_time",
            "out_time",
            "attendance_type",
            "location",
            "latitude",       # ✅ instead of location
            "longitude", 
            "qr_scan",
            "selfie",
            "status",
            "verified_by",
            "created_at",
            "updated_at",
            "punch_in",
        ]

    def get_latitude(self, obj):
        if obj.qrsession:
            return obj.qrsession.latitudes
        return None

    def get_longitude(self, obj):
        if obj.qrsession:
            return obj.qrsession.longitude
        return None

    def get_in_time(self, obj):
        if obj.in_time:
            # Format: "YYYY-MM-DD HH:MM:SS"
            return obj.in_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        return None

    def get_out_time(self, obj):
        if obj.out_time:
            return obj.out_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        return None



# leave list serializer 
class LeaveSerializerview(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    approved_by = serializers.StringRelatedField()

    class Meta:
        model = Leave
        fields = '__all__'

# Employee Daily Attendance Details Serializer
class EmployeeDailyAttendanceDetailsSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    session_duration_hours = serializers.SerializerMethodField()
    is_active_session = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'department', 'designation',
            'date', 'in_time', 'out_time', 'attendance_type', 'location', 
            'qr_scan', 'status', 'punch_in', 'session_duration_hours', 
            'is_active_session', 'created_at', 'updated_at'
        ]
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def get_employee_id(self, obj):
        return obj.employee.employee_id
    
    def get_department(self, obj):
        return obj.employee.department
    
    def get_designation(self, obj):
        return obj.employee.designation
    
    def get_session_duration_hours(self, obj):
        if obj.out_time and obj.in_time:
            duration = obj.out_time - obj.in_time
            return round(duration.total_seconds() / 3600, 2)
        return None
    
    def get_is_active_session(self, obj):
        return obj.out_time is None and obj.punch_in        
    
    
    
    
    
class TaskWithProjectSerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    project_details = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "assigned_by_name",
            "assigned_to_name",
            "created_at",
            "updated_at",
            "project_details",
        ]

    def get_assigned_by_name(self, obj):
        if obj.assigned_by and obj.assigned_by.employee_profile:
            return f"{obj.assigned_by.employee_profile.first_name} {obj.assigned_by.employee_profile.last_name}"
        return obj.assigned_by.email if obj.assigned_by else None

    def get_assigned_to_name(self, obj):
        if obj.assigned_to and obj.assigned_to.employee_profile:
            return f"{obj.assigned_to.employee_profile.first_name} {obj.assigned_to.employee_profile.last_name}"
        return obj.assigned_to.email if obj.assigned_to else None

    def get_project_details(self, obj):
        if obj.project:
            return {
                "id": obj.project.id,
                "project_name": obj.project.project_name,
                "client": obj.project.client,
                "start_date": obj.project.start_date,
                "end_date": obj.project.end_date,
                "priority": obj.project.priority,
                "project_value": obj.project.project_value,
                "total_working_hours": obj.project.total_working_hours,
                "extra_time": obj.project.extra_time,
                "description": obj.project.description,
                "status": obj.project.status,
                "project_logo": obj.project.project_logo.url if obj.project.project_logo else None,
                "attachment": obj.project.attachment.url if obj.project.attachment else None,
            }
        return None   
    
    
    
    
class FaceAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "status"]    
        
        
        
        
# employee notification serializer 
       
                     
class TaskSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = Task
        fields = ["id","title", "due_date","description", "assigned_by", "assigned_to", "status"]   
        
        
        
        
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
   # purpose = serializers.ChoiceField(choices=[("login", "login"),])    
   
   
   
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = [
            "id",
            "user",
            "action",
            "timestamp",
        ]
           
                     
# Project Member Serializer
# ---------------------------
class ProjectMembersReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMembers
        fields = ["team_leader", "project_manager", "tags"]

from datetime import datetime, date,time
from django.utils.timezone import is_aware, make_naive


# ---------------------------
# Task Serializer (limited)
# ---------------------------
# ---------------------------
# Task Serializer (limited)
# ---------------------------
# Task Serializer (limited)
# ---------------------------
class LimitedTaskSerializer(serializers.ModelSerializer):
    task_hours = serializers.SerializerMethodField()
    current_progress = serializers.SerializerMethodField()
    assigned_employee = serializers.SerializerMethodField()  # ✅ New field

    class Meta:
        model = Task
        fields = ["task_hours", "current_progress", "assigned_employee"]

    def _to_datetime(self, dt):
        """Convert date to datetime and make timezone naive if needed."""
        if isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, time.min)  # convert date → datetime
        if is_aware(dt):
            dt = make_naive(dt)  # only convert aware → naive
        return dt

    def get_task_hours(self, obj):
        """Total available hours between created_at and due_date."""
        if obj.created_at and obj.due_date:
            start = self._to_datetime(obj.created_at)
            end = self._to_datetime(obj.due_date)
            delta = end - start
            return round(delta.total_seconds() / 3600, 2)
        return None

    def get_current_progress(self, obj):
        """Shows how much time has passed (in hours and percentage)."""
        if obj.created_at and obj.due_date:
            start = self._to_datetime(obj.created_at)
            end = self._to_datetime(obj.due_date)

            total_seconds = (end - start).total_seconds()
            elapsed_seconds = (self._to_datetime(now()) - start).total_seconds()

            if total_seconds <= 0:
                return "0 / 0 hours (0%)"

            progress_fraction = elapsed_seconds / total_seconds
            progress_fraction = max(0.0, min(progress_fraction, 1.0))  # clamp 0–1

            total_hours = round(total_seconds / 3600, 2)
            current_hours = round(elapsed_seconds / 3600, 2)
            return f"{current_hours} / {total_hours} hours ({round(progress_fraction * 100, 1)}%)"
        return None

    def get_assigned_employee(self, obj):
        """Return assigned employee info."""
        if not obj.assigned_to:
            return None
        try:
            emp = EmployeeDetail.objects.get(user=obj.assigned_to)
            request = self.context.get("request")
            return {
                "id": emp.id,
                "user_id": emp.user.id,
                "name": f"{emp.first_name} {emp.last_name}",
                "designation": emp.designation,
                "profile_pic": request.build_absolute_uri(emp.profile_pic.url) if request and emp.profile_pic else None,
            }
        except EmployeeDetail.DoesNotExist:
            return None 
# ---------------------------
# Project Members Read Serializer
# ---------------------------
class NewProjectMembersReadSerializer(serializers.ModelSerializer):
    # team_members = serializers.SerializerMethodField()
    project_manager_details = serializers.SerializerMethodField()
    team_leader_details = serializers.SerializerMethodField()
    tags_details = serializers.SerializerMethodField()

    class Meta:
        model = ProjectMembers
        fields = [
            "team_leader_details",
            "project_manager_details",
            "tags_details",
            # "team_members"
        ]

    # -------------------------------
    # Helper to get full employee info
    # -------------------------------
    def get_employee_info(self, emp_id):
    # """Return basic employee info (id, name, designation, profile_pic)."""
      try:
          emp = EmployeeDetail.objects.get(user=emp_id)
          request = self.context.get("request")  # safer
          return {
              "id": emp.id,
              "user_id": emp.user.id,
              "name": f"{emp.first_name} {emp.last_name}",
              "designation": emp.designation,
              "profile_pic": request.build_absolute_uri(emp.profile_pic.url) if request and emp.profile_pic else None,
          }
      except EmployeeDetail.DoesNotExist:
          return None


    # --------------------------------
    # Project Manager (Coordinator)
    # --------------------------------
    def get_project_manager_details(self, obj):
        data = obj.project_manager
        if not data:
            return None

        if isinstance(data, dict):
            emp_id = data.get("id")
        elif isinstance(data, int):
            emp_id = data
        else:
            emp_id = None

        return self.get_employee_info(emp_id)

    # --------------------------------
    # Team Leader
    # --------------------------------
    def get_team_leader_details(self, obj):
        data = obj.team_leader
        if not data:
            return None

        if isinstance(data, dict):
            emp_id = data.get("id")
        elif isinstance(data, int):
            emp_id = data
        else:
            emp_id = None

        return self.get_employee_info(emp_id)
    
    def get_tags_details(self , obj):
        data = obj.tags
        if not data:
            return None
        if isinstance(data, dict):
            emp_id = data.get("id")
        elif isinstance(data, int):
            emp_id = data
        else:
            emp_id = None
        return self.get_employee_info(emp_id)    


    # --------------------------------
    # Team Members with assigned tasks
    # --------------------------------
    # def get_team_members(self, obj):
    #     project = obj.project
    #     members_list = []

    #     # Collect IDs from tags (which store team members)
    #     tag_data = obj.tags or []
    #     if not isinstance(tag_data, list):
    #         return []

    #     for member in tag_data:
    #         if isinstance(member, dict):
    #             emp_id = member.get("id")
    #         elif isinstance(member, int):
    #             emp_id = member
    #         else:
    #             emp_id = None

    #         emp_info = self.get_employee_info(emp_id)
    #         if emp_info:
    #             # Find tasks assigned to this employee’s user
    #             tasks = Task.objects.filter(
    #                 project=project,
    #                 assigned_to=emp_info["user"]
    #             ).values("title", "status")

    #             emp_info["assigned_tasks"] = list(tasks)
    #             members_list.append(emp_info)

    #     return members_list


# ---------------------------
# Project Serializer (limited)
# ---------------------------
class NewProjectReadSerializer(serializers.ModelSerializer):
    members = NewProjectMembersReadSerializer(source="projectmembers_set", many=True, read_only=True)
    tasks = serializers.SerializerMethodField()
    coordinator = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "project_name",
            "start_date",
            "end_date",
            "status",
            "coordinator",  # ✅ Project Manager
            "members",       # ✅ Team + Leader
            "tasks",
        ]

    def get_coordinator(self, obj):
        """Fetch project manager from ProjectMembers JSON by ID."""
        project_member = ProjectMembers.objects.filter(project=obj).first()
        if project_member:
            return NewProjectMembersReadSerializer(
                project_member, context=self.context
            ).data.get("project_manager_details")
        return None

    def get_tasks(self, obj):
        tasks = obj.task_set.all().order_by("-id")
        return LimitedTaskSerializer(tasks, many=True).data
    
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "is_active",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()    
    
    
    
class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'receiver', 'message', 'is_read', 'timestamp']


class ChatThreadSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)
    messages = ChatMessageSerializer(many=True, source='chatmessage_set', read_only=True)

    class Meta:
        model = ChatThread
        fields = ['id', 'user1', 'user2', 'updated_at', 'messages']
    
