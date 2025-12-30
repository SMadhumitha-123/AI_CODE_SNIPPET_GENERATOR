Here's a C code snippet to reverse a string with detailed explanation:

## Method 1: In-place reversal using two pointers

```c
#include <stdio.h>
#include <string.h>

void reverseString(char str[]) {
    int start = 0;
    int end = strlen(str) - 1;
    char temp;
    
    // Swap characters from both ends moving towards center
    while (start < end) {
        // Swap characters at start and end positions
        temp = str[start];
        str[start] = str[end];
        str[end] = temp;
        
        // Move pointers towards center
        start++;
        end--;
    }
}

int main() {
    char str[] = "Hello World";
    
    printf("Original string: %s\n", str);
    
    reverseString(str);
    
    printf("Reversed string: %s\n", str);
    
    return 0;
}
```

## Method 2: Using recursion

```c
#include <stdio.h>
#include <string.h>

void reverseStringRecursive(char str[], int start, int end) {
    char temp;
    
    // Base case: when start >= end, we've reached the middle
    if (start >= end) {
        return;
    }
    
    // Swap characters at start and end positions
    temp = str[start];
    str[start] = str[end];
    str[end] = temp;
    
    // Recursive call with updated positions
    reverseStringRecursive(str, start + 1, end - 1);
}

int main() {
    char str[] = "Programming";
    int length = strlen(str);
    
    printf("Original string: %s\n", str);
    
    reverseStringRecursive(str, 0, length - 1);
    
    printf("Reversed string: %s\n", str);
    
    return 0;
}
```

## Complete example with user input:

```c
#include <stdio.h>
#include <string.h>

void reverseString(char str[]) {
    int start = 0;
    int end = strlen(str) - 1;
    char temp;
    
    while (start < end) {
        temp = str[start];
        str[start] = str[end];
        str[end] = temp;
        start++;
        end--;
    }
}

int main() {
    char str[100];
    
    printf("Enter a string: ");
    fgets(str, sizeof(str), stdin);
    
    // Remove newline character if present
    str[strcspn(str, "\n")] = '\0';
    
    printf("Original string: %s\n", str);
    
    reverseString(str);
    
    printf("Reversed string: %s\n", str);
    
    return 0;
}
```

#