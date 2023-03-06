
(define-macro (def func args body)
  (list 'define (cons func args) body)
)


(define (map-stream f s)
    (if (null? s)
    	nil
    	(cons-stream (f (car s)) (map-stream f (cdr-stream s)))))

(define all-three-multiples
  (cons-stream 3 (map-stream (lambda (x) (+ x 3)) all-three-multiples))
)


(define (compose-all funcs)
  (if (null? funcs)
    (lambda (x) x)
    (lambda (x) ((compose-all (cdr funcs)) ((car funcs) x)))
  )
)


(define (partial-sums stream)
  (define (helper sum stream)
    (if (null? stream)
      nil
      (let ((new_sum (+ sum (car stream))))
        (cons-stream new_sum (helper new_sum (cdr-stream stream)))
      )
    )
  )
  (helper 0 stream)
)

