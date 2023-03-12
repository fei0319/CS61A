(define (split-at lst n)
  (if (or (eq? n 0) (null? lst))
	(cons nil lst)
	(let ((next (split-at (cdr lst) (- n 1))))
		(cons (cons (car lst) (car next)) (cdr next))
	)
  )
)


(define-macro (switch expr cases)
	(cons 'cond
		(map (lambda (case) (cons (eq? (eval expr) (car case)) (cdr case)))
    			cases)
	)
)