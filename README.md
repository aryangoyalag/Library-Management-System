# Library-Management-System

## FastAPI Documentation

### Endpoints

#### User

| Method | Endpoint                | Summary              | Parameters                                                                                                                                                                                                 | Responses |
|--------|-------------------------|----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| POST   | /User/create_user       | Create User          | - `first_name`: string (required) <br> - `last_name`: string (required) <br> - `email`: string (required) <br> - `password`: string (required) <br> - `role`: string (optional, default: "Member")         | - 200: Successful Response <br> - 422: Validation Error |
| GET    | /User                   | Get User Details     | -                                                                                                                                                                                                         | - 200: Successful Response |
| PUT    | /User/update_user       | Update User Details  | - `password`: string (required) <br> - `first_name`: string (optional) <br> - `last_name`: string (optional) <br> - `new_password`: string (optional)                                                     | - 200: Successful Response <br> - 422: Validation Error |
| DELETE | /User/delete_user       | Delete User          | - `password`: string (required)                                                                                                                                                                           | - 200: Successful Response <br> - 422: Validation Error |

#### Notifications

| Method | Endpoint                               | Summary                | Parameters                                            | Responses |
|--------|----------------------------------------|------------------------|------------------------------------------------------|-----------|
| GET    | /notifications                         | Get Notifications      | -                                                    | - 200: Successful Response |
| PUT    | /notifications/{notification_id}/read  | Mark Notification As Read | - `notification_id`: integer (required)                | - 200: Successful Response <br> - 422: Validation Error |

#### Loan

| Method | Endpoint                           | Summary              | Parameters                                      | Responses |
|--------|------------------------------------|----------------------|------------------------------------------------|-----------|
| POST   | /loan/librarian/check_overdue_loans | Check Overdue Loans   | -                                              | - 200: Successful Response |
| POST   | /loan/User/create_loan              | Create Loan           | - `rent_title`: string (required)              | - 200: Successful Response <br> - 422: Validation Error |
| POST   | /loan/User/cancel_loan              | Cancel Loan           | - `loan_id`: integer (required)                | - 200: Successful Response <br> - 422: Validation Error |
| POST   | /loan/User/return_book              | Return Book           | - `loan_id`: integer (required)                | - 200: Successful Response <br> - 422: Validation Error |
| POST   | /loan/librarian/approve_loan        | Approve Loan          | - `LoanApprovalRequest`: object (required)     | - 200: Successful Response <br> - 422: Validation Error |
| POST   | /loan/librarian/cancel_loan         | Cancel Loan           | - `LoanCancellationRequest`: object (required) | - 200: Successful Response <br> - 422: Validation Error |
| POST   | /loan/librarian/return_book         | Return Book           | - `LoanReturnRequest`: object (required)       | - 200: Successful Response <br> - 422: Validation Error |

#### Book

| Method | Endpoint               | Summary        | Parameters                                                                                     | Responses |
|--------|------------------------|----------------|-----------------------------------------------------------------------------------------------|-----------|
| GET    | /book/search_books     | Search Books   | - `title`: string (optional) <br> - `author`: string (optional) <br> - `genre`: string (optional) | - 200: Successful Response <br> - 422: Validation Error |
| POST   | /book/create_book      | Create Book    | - `BookCreate`: object (required)                                                             | - 200: Successful Response <br> - 422: Validation Error |
| DELETE | /book/delete_book/{id} | Delete Book    | - `id`: integer (required)                                                                    | - 200: Successful Response <br> - 422: Validation Error |
| PUT    | /book/update_book/{id} | Update Book    | - `id`: integer (required) <br> - `title`: string (optional) <br> - `pages`: integer (optional) <br> - `total_copies`: integer (optional) | - 200: Successful Response <br> - 422: Validation Error |

#### Author

| Method | Endpoint                      | Summary             | Parameters                                      | Responses |
|--------|-------------------------------|---------------------|------------------------------------------------|-----------|
| GET    | /Author/search_by_pen_name    | Search By Pen Name  | - `pen_name`: string (required)                | - 200: Successful Response <br> - 422: Validation Error |
| POST   | /Author/create_author         | Create Author       | - `AuthorCreate`: object (required)            | - 200: Successful Response <br> - 422: Validation Error |
| PUT    | /Author/update_author/{author_id} | Update Author     | - `author_id`: integer (required) <br> - `AuthorUpdate`: object (required) | - 200: Successful Response <br> - 422: Validation Error |
| DELETE | /Author/delete_author/{author_id} | Delete Author     | - `author_id`: integer (required)              | - 200: Successful Response <br> - 422: Validation Error |

#### Miscellaneous

| Method | Endpoint | Summary  | Parameters | Responses |
|--------|----------|----------|------------|-----------|
| GET    | /        | Index    | -          | - 200: Successful Response |
| POST   | /login   | Login    | - `Body_login_login_post`: object (required) | - 200: Successful Response <br> - 422: Validation Error |

