(define (caar x) (car (car x)))
(define (cadr x) (car (cdr x)))
(define (cdar x) (cdr (car x)))
(define (cddr x) (cdr (cdr x)))

; Some utility functions that you may find useful to implement.

(define (cons-all first rests)
  (define (fn lst)
    (cons first lst)
  )
  (map fn rests)
)

(define (zip pairs)
  (define (zip-to a b pairs)
    (if (null? pairs)
      `(,a ,b)
      (let ((pair (car pairs)))
        (zip-to (cons (car pair) a) (cons (cadr pair) b) (cdr pairs))
      )
    )
  )
  (define (reverse s)
    (define (reverse-to s start)
      (if (null? s)
        start
        (reverse-to (cdr s) (cons (car s) start))
      )
    )
    (reverse-to s nil)
  )
  (map reverse (zip-to nil nil pairs))
)

;; Problem 17
;; Returns a list of two-element lists
(define (enumerate s)
  ; BEGIN PROBLEM 17
  (define (enumerate-index s id) 
    (if (null? s)
      nil
      (cons (list id (car s)) (enumerate-index (cdr s) (+ id 1)))
    )
  )
  (enumerate-index s 0)
)
  ; END PROBLEM 17

;; Problem 18
;; List all ways to make change for TOTAL with DENOMS
(define (list-change total denoms)
  ; BEGIN PROBLEM 18
  (if (or (null? denoms) (< total 0))
    nil
    (if (= total 0)
      (list nil)
      (append (cons-all (car denoms) (list-change (- total (car denoms)) denoms)) (list-change total (cdr denoms)))
    )
  )
)
  ; END PROBLEM 18

;; Problem 19
;; Returns a function that checks if an expression is the special form FORM
(define (check-special form)
  (lambda (expr) (equal? form (car expr))))

(define lambda? (check-special 'lambda))
(define define? (check-special 'define))
(define quoted? (check-special 'quote))
(define let?    (check-special 'let))

;; Converts all let special forms in EXPR into equivalent forms using lambda
(define (let-to-lambda expr)
  (cond ((atom? expr)
         ; BEGIN PROBLEM 19
         expr
         ; END PROBLEM 19
         )
        ((quoted? expr)
         ; BEGIN PROBLEM 19
         expr
         ; END PROBLEM 19
         )
        ((or (lambda? expr)
             (define? expr))
         (let ((form   (car expr))
               (params (cadr expr))
               (body   (cddr expr)))
           ; BEGIN PROBLEM 19
           (append (list form params) (map let-to-lambda body))
           ; END PROBLEM 19
           ))
        ((let? expr)
         (let ((values (cadr expr))
               (body   (cddr expr)))
           ; BEGIN PROBLEM 19)
            (let ((bindings (zip values)))
              (cons (append `(lambda ,(car bindings)) (map let-to-lambda body)) (map let-to-lambda (cadr bindings)))
            )
           ; END PROBLEM 19
           ))
        (else
         ; BEGIN PROBLEM 19
         (map let-to-lambda expr)
         ; END PROBLEM 19
         )))
