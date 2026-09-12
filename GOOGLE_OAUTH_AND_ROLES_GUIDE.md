# Midad LMS: Role Segregation & Google SSO Setup Guide

This guide explains how to secure your website so that:
1. **You (The Owner/Admin)** have exclusive full access to Desk, website customization, and billing.
2. **Invited Creators/Instructors** can ONLY upload courses, add lessons, and build quizzes (with zero access to website editing or settings).
3. **Google Sign-Up/Sign-In** is enabled for all users and students.

---

## 1. User Roles & Access Architecture

In Frappe LMS, permissions are divided cleanly by roles:

| User Type | Frappe Roles Assigned | Permitted Actions | Forbidden Actions |
| :--- | :--- | :--- | :--- |
| **Owner (You)** | `System Manager`, `Administrator`, `LMS Moderator` | Everything: website branding, payment accounts, user roles, database, all courses. | None |
| **Course Creators** | `LMS Instructor`, `Course Moderator` | Create courses, upload 10 GB videos, write lessons, make quizzes, review submissions. | **Cannot** touch website theme, cannot edit website pages, cannot see billing keys, cannot edit other instructors' private courses. |
| **Students / Public** | `LMS Student`, `Website User` | Browse catalog, enroll in free Microbiology course, purchase Anatomy & Physiology, take quizzes. | Cannot edit courses, cannot access instructor studio, cannot access `/app` desk. |

---

## 2. How to Invite an Existing Student to Become a Course Creator

When someone signs up on Midad (via email or Google), they start with the default **Student** role.

### To promote them to a Course Creator (with no website edit rights):
1. Log in to your Admin Desk: `http://<your-domain>/app`
2. In the top search bar (Awesome Bar), type **User List** and press `Enter`.
3. Click on the student's email address.
4. Scroll down to the **Roles** table.
5. Check the box for:
   * **`LMS Instructor`** (or **`Course Moderator`**)
   * Make sure **`System Manager`** and **`Website Manager`** remain **UNCHECKED**.
6. Click **Save** in the top right.

> [!TIP]
> That user can now go to `http://<your-domain>/lms` and will see the **"+ Create Course"** and **"Studio"** buttons. However, if they try to go to `/app` or edit website settings, Frappe will automatically reject them with `403 Not Permitted`.

---

## 3. Setting Up "Sign in with Google" (Google OAuth 2.0)

To allow students and creators to sign up with one click using their Google account:

### Step 1: Create Credentials in Google Cloud Console
1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project named `Midad LMS`.
3. Go to **APIs & Services** $\rightarrow$ **OAuth consent screen**:
   * User Type: **External**
   * App name: `Midad Medical LMS`
   * User support email: `your-email@example.com`
4. Go to **APIs & Services** $\rightarrow$ **Credentials**:
   * Click **+ Create Credentials** $\rightarrow$ **OAuth client ID**.
   * Application type: **Web application**.
   * Name: `Midad Web Client`.
   * **Authorized JavaScript origins**:
     `https://<your-domain>` (or `http://localhost:8000` for local testing)
   * **Authorized redirect URIs**:
     `https://<your-domain>/api/method/frappe.integrations.oauth2_logins.custom/google`
5. Copy your **Client ID** and **Client Secret**.

### Step 2: Configure Google in Frappe Desk
1. In Frappe Desk (`http://<your-domain>/app`), search for **Social Login Key List**.
2. Click on **Google**.
3. Fill in:
   * **Client ID**: Paste your Google Client ID.
   * **Client Secret**: Paste your Google Client Secret.
   * **Enable Social Login**: Check this box (`Enabled`).
4. Click **Save**.

The **"Continue with Google"** button will now automatically appear on the Midad login and sign-up modals!
