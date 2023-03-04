(define (cddr s)
  (cdr (cdr s)))

(define (cadr s)
  (car (cdr s))
)

(define (caddr s)
  (cadr (cdr s))
)


(define (sign num)
  (cond
  ((> num 0) 1)
  ((< num 0) -1)
  (else 0)
  )
)


(define (square x) (* x x))

(define (pow x y)
  (if (= y 0)
    1
    (if (= (* (quotient y 2) 2) y)
      (pow (square x) (quotient y 2))
      (* (pow (square x) (quotient y 2)) x)
    )
  )
)


(define (unique s)
  (if (null? s)
    nil
    (cons (car s) (unique (filter (lambda (x) (not (eq? x (car s)))) (cdr s))))
  )
)


(define (replicate x n)
  (define (replicate-to x n s)
    (if (= n 0)
      s
      (replicate-to x (- n 1) (cons x s))
    )
  )
  (replicate-to x n nil)
)


(define (accumulate combiner start n term)
  (define (range-accumulate l r start)
    (if (> l r)
      start
      (range-accumulate (+ l 1) r (combiner start (term l)))
    )
  )
  (range-accumulate 1 n start)
)


(define (accumulate-tail combiner start n term)
  (accumulate combiner start n term)
)


(define-macro (list-of map-expr for var in lst if filter-expr)
  (list 'map (list 'lambda (list var) map-expr) (list 'filter (list 'lambda (list var) filter-expr) lst))
)

