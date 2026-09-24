import Swal from "sweetalert2";

export const SwalMixin = Swal.mixin({
  customClass: {
    confirmButton: "btn btn-success",
    cancelButton: "btn btn-danger"
  }
})
