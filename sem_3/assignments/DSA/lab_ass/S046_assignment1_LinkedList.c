#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node *next;
} Node;

/* Function prototypes */
void insertAtBeginning(Node **head, int value);
void insertAtEnd(Node **head, int value);
void insertAtPosition(Node **head, int value, int position);

void deleteFromBeginning(Node **head);
void deleteFromEnd(Node **head);
void deleteFromPosition(Node **head, int position);

void search(Node *head, int value);
void display(Node *head);
void freeList(Node **head);

/* Insert at the beginning */
void insertAtBeginning(Node **head, int value) {
    Node *newNode = (Node *)malloc(sizeof(Node));

    if (newNode == NULL) {
        printf("Memory allocation failed.\n");
        return;
    }

    newNode->data = value;
    newNode->next = *head;
    *head = newNode;

    printf("Node inserted at the beginning.\n");
}

/* Insert at the end */
void insertAtEnd(Node **head, int value) {
    Node *newNode = (Node *)malloc(sizeof(Node));
    Node *temp;

    if (newNode == NULL) {
        printf("Memory allocation failed.\n");
        return;
    }

    newNode->data = value;
    newNode->next = NULL;

    if (*head == NULL) {
        *head = newNode;
        printf("Node inserted at the end.\n");
        return;
    }

    temp = *head;

    while (temp->next != NULL) {
        temp = temp->next;
    }

    temp->next = newNode;

    printf("Node inserted at the end.\n");
}

/* Insert at a specific position */
void insertAtPosition(Node **head, int value, int position) {
    Node *newNode;
    Node *temp;
    int i;

    if (position < 1) {
        printf("Invalid position. Position must be 1 or greater.\n");
        return;
    }

    if (position == 1) {
        insertAtBeginning(head, value);
        return;
    }

    temp = *head;

    for (i = 1; i < position - 1 && temp != NULL; i++) {
        temp = temp->next;
    }

    if (temp == NULL) {
        printf("Invalid position.\n");
        return;
    }

    newNode = (Node *)malloc(sizeof(Node));

    if (newNode == NULL) {
        printf("Memory allocation failed.\n");
        return;
    }

    newNode->data = value;
    newNode->next = temp->next;
    temp->next = newNode;

    printf("Node inserted at position %d.\n", position);
}

/* Delete from the beginning */
void deleteFromBeginning(Node **head) {
    Node *temp;

    if (*head == NULL) {
        printf("Linked list is empty. Nothing to delete.\n");
        return;
    }

    temp = *head;
    *head = (*head)->next;

    printf("Deleted node: %d\n", temp->data);
    free(temp);
}

/* Delete from the end */
void deleteFromEnd(Node **head) {
    Node *temp;
    Node *previous;

    if (*head == NULL) {
        printf("Linked list is empty. Nothing to delete.\n");
        return;
    }

    if ((*head)->next == NULL) {
        printf("Deleted node: %d\n", (*head)->data);
        free(*head);
        *head = NULL;
        return;
    }

    previous = NULL;
    temp = *head;

    while (temp->next != NULL) {
        previous = temp;
        temp = temp->next;
    }

    previous->next = NULL;

    printf("Deleted node: %d\n", temp->data);
    free(temp);
}

/* Delete from a specific position */
void deleteFromPosition(Node **head, int position) {
    Node *temp;
    Node *nodeToDelete;
    int i;

    if (*head == NULL) {
        printf("Linked list is empty. Nothing to delete.\n");
        return;
    }

    if (position < 1) {
        printf("Invalid position. Position must be 1 or greater.\n");
        return;
    }

    if (position == 1) {
        deleteFromBeginning(head);
        return;
    }

    temp = *head;

    for (i = 1; i < position - 1 && temp != NULL; i++) {
        temp = temp->next;
    }

    if (temp == NULL || temp->next == NULL) {
        printf("Invalid position.\n");
        return;
    }

    nodeToDelete = temp->next;
    temp->next = nodeToDelete->next;

    printf("Deleted node: %d\n", nodeToDelete->data);
    free(nodeToDelete);
}

/* Search for an element */
void search(Node *head, int value) {
    Node *temp = head;
    int position = 1;

    if (head == NULL) {
        printf("Linked list is empty.\n");
        return;
    }

    while (temp != NULL) {
        if (temp->data == value) {
            printf("%d found at position %d.\n", value, position);
            return;
        }

        temp = temp->next;
        position++;
    }

    printf("%d not found in the linked list.\n", value);
}

/* Display the linked list */
void display(Node *head) {
    Node *temp = head;

    if (head == NULL) {
        printf("Linked List: EMPTY\n");
        return;
    }

    printf("Linked List: ");

    while (temp != NULL) {
        printf("%d", temp->data);

        if (temp->next != NULL) {
            printf(" -> ");
        }

        temp = temp->next;
    }

    printf(" -> NULL\n");
}

/* Free all remaining nodes before program exits */
void freeList(Node **head) {
    Node *temp;

    while (*head != NULL) {
        temp = *head;
        *head = (*head)->next;
        free(temp);
    }
}

int main(void) {
    Node *head = NULL;
    int choice;
    int value;
    int position;

    do {
        printf("\n========== SINGLY LINKED LIST MENU ==========\n");
        printf("1. Insert at beginning\n");
        printf("2. Insert at end\n");
        printf("3. Insert at specific position\n");
        printf("4. Delete from beginning\n");
        printf("5. Delete from end\n");
        printf("6. Delete from specific position\n");
        printf("7. Search for an element\n");
        printf("8. Display linked list\n");
        printf("9. Exit\n");
        printf("Enter your choice: ");

        if (scanf("%d", &choice) != 1) {
            printf("Invalid input.\n");

            while (getchar() != '\n') {
                /* Clear invalid input */
            }

            continue;
        }

        switch (choice) {
            case 1:
                printf("Enter value to insert: ");
                scanf("%d", &value);

                insertAtBeginning(&head, value);
                display(head);
                break;

            case 2:
                printf("Enter value to insert: ");
                scanf("%d", &value);

                insertAtEnd(&head, value);
                display(head);
                break;

            case 3:
                printf("Enter value to insert: ");
                scanf("%d", &value);

                printf("Enter position: ");
                scanf("%d", &position);

                insertAtPosition(&head, value, position);
                display(head);
                break;

            case 4:
                deleteFromBeginning(&head);
                display(head);
                break;

            case 5:
                deleteFromEnd(&head);
                display(head);
                break;

            case 6:
                printf("Enter position to delete: ");
                scanf("%d", &position);

                deleteFromPosition(&head, position);
                display(head);
                break;

            case 7:
                printf("Enter element to search: ");
                scanf("%d", &value);

                search(head, value);
                break;

            case 8:
                display(head);
                break;

            case 9:
                printf("Exiting program.\n");
                break;

            default:
                printf("Invalid choice. Please enter a number from 1 to 9.\n");
        }

    } while (choice != 9);

    freeList(&head);

    return 0;
}
